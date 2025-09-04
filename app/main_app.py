import streamlit as st
import pandas as pd
import os
import pickle
from sklearn.impute import SimpleImputer

# --- Importações do Projeto ---
from core.data.io import read_csv_smart
from core.data.database import (
    create_database_and_tables,
    insert_csv_to_sor,
    run_etl_sor_to_sot,
    run_etl_sot_to_spec_train,
    run_etl_for_test_data,
    load_data,
    drop_database
)
from core.features.preprocess import make_preprocess_pipeline
from core.models.train import train_regressor
from core.models.predict import evaluate_regressor
from core.explain.coefficients import extract_linear_importances
from core.chatbot.rules import answer_from_metrics

# --- Configurações da Página e Estado ---
st.set_page_config(page_title="Análise de Empréstimo", layout="wide")

if "model_trained" not in st.session_state:
    st.session_state.model_trained = False
if "predictions_made" not in st.session_state:
    st.session_state.predictions_made = False
if "prediction_df" not in st.session_state:
    st.session_state.prediction_df = None
if "chat_messages" not in st.session_state:
    st.session_state.chat_messages = [{"role": "assistant", "content": "Olá! Treine um modelo ou carregue um modelo salvo para começar."}]
if "metrics" not in st.session_state:
    st.session_state.metrics = None
if "importances" not in st.session_state:
    st.session_state.importances = None

# --- Diretórios ---
MODEL_DIR = "model"
if not os.path.exists(MODEL_DIR):
    os.makedirs(MODEL_DIR)
MODEL_PATH = os.path.join(MODEL_DIR, "regressor_model.pickle")

# --- Funções Auxiliares ---
@st.cache_data
def convert_df_to_csv(df):
    return df.to_csv(index=False).encode('utf-8')

# --- Título e Sidebar ---
st.title("🧪 Pipeline de Previsão de Empréstimo")

with st.sidebar:
    st.header("1. Upload dos Dados")
    uploaded_files = st.file_uploader(
        "Envie 'Train.csv' (para treino) e/ou 'Test.csv' (para previsão)",
        type=["csv"],
        accept_multiple_files=True
    )
    
    st.header("2. Ações do Pipeline")
    
    # --- Treinar Novo Modelo ---
    st.subheader("Treinar Novo Modelo")
    test_size = st.slider("Tamanho do conjunto de teste (validação)", 0.1, 0.4, 0.2, 0.05)
    if st.button("Executar Treinamento"):
        df_train = None
        for file in uploaded_files:
            if "train" in file.name.lower():
                df_train = read_csv_smart(file)
        
        if df_train is not None:
            with st.spinner("Treinando o modelo..."):
                create_database_and_tables()
                insert_csv_to_sor(df_train)
                run_etl_sor_to_sot()
                run_etl_sot_to_spec_train()
                df_spec_train = load_data("spec_emprestimo_train")
                
                # --- Target e Features ---
                target = "Loan_Status"
                y = df_spec_train[target].map({'Y': 1, 'N': 0})  # Convertendo target
                X = df_spec_train.drop(columns=[target])
                
                # --- Corrigindo colunas especiais ---
                X['Dependents'] = X['Dependents'].replace('3+', 3).astype(float)
                X['Credit_History'] = X['Credit_History'].replace({'N': 0, 'Y': 1}).astype(float)
                
                # --- Imputação de valores faltantes ---
                num_cols = ['Dependents', 'ApplicantIncome', 'CoapplicantIncome', 
                            'LoanAmount', 'Loan_Amount_Term', 'Credit_History']
                num_imputer = SimpleImputer(strategy='mean')
                X[num_cols] = num_imputer.fit_transform(X[num_cols])
                
                # --- Pipeline e Treino ---
                pre = make_preprocess_pipeline(X)
                model, X_test, y_test = train_regressor(X, y, pre, test_size=test_size)
                
                with open(MODEL_PATH, "wb") as f:
                    pickle.dump(model, f)
                
                st.session_state.metrics = evaluate_regressor(model, X_test, y_test)
                st.session_state.importances = extract_linear_importances(model, X.columns, pre)
                st.session_state.model_trained = True
                st.session_state.predictions_made = False
            st.success("Modelo treinado e salvo com sucesso!")
        else:
            st.warning("Arquivo 'Train.csv' não encontrado.")

    # --- Usar Modelo Existente ---
    st.subheader("Usar Modelo Existente")
    if st.button("Carregar Modelo e Fazer Previsões"):
        if not os.path.exists(MODEL_PATH):
            st.error("Nenhum modelo treinado foi encontrado! Execute o treinamento primeiro.")
        else:
            df_test = None
            for file in uploaded_files:
                if "test" in file.name.lower():
                    df_test = read_csv_smart(file)
            
            if df_test is not None:
                with st.spinner("Carregando modelo e fazendo previsões..."):
                    run_etl_for_test_data(df_test)
                    df_spec_predict = load_data("spec_emprestimo_predict")
                    
                    # --- Corrigindo colunas especiais ---
                    df_spec_predict['Dependents'] = df_spec_predict['Dependents'].replace('3+', 3).astype(float)
                    df_spec_predict['Credit_History'] = df_spec_predict['Credit_History'].replace({'N': 0, 'Y': 1}).astype(float)
                    df_spec_predict[num_cols] = num_imputer.transform(df_spec_predict[num_cols])
                    
                    with open(MODEL_PATH, 'rb') as f:
                        model = pickle.load(f)

                    ids = df_spec_predict[['Loan_ID']]
                    X_predict = df_spec_predict.drop(columns=['Loan_ID'])
                    predictions = model.predict(X_predict)
                    
                    result_df = ids.copy()
                    result_df['Loan_Status'] = predictions
                    st.session_state.prediction_df = result_df
                    st.session_state.predictions_made = True
                st.success("Previsões geradas com sucesso!")
            else:
                st.warning("Arquivo 'Test.csv' não encontrado.")
    
    # --- Limpeza ---
    st.header("3. Manutenção")
    if st.button("Limpar Tudo"):
        drop_database()
        if os.path.exists(MODEL_PATH):
            os.remove(MODEL_PATH)
        st.session_state.clear()
        st.info("Banco de dados, modelo salvo e sessão resetados.")
        st.rerun()

# --- Abas ---
tab_train, tab_predict, tab_chat = st.tabs(["📊 Resultados do Treino", "🚀 Previsões", "💬 Chat com o Modelo"])

with tab_train:
    st.header("Métricas e Importância do Modelo")
    if not st.session_state.model_trained:
        st.info("Treine um modelo para ver os resultados.")
    else:
        st.subheader("📈 Métricas")
        st.json(st.session_state.metrics)
        st.subheader("🔎 Importâncias")
        st.dataframe(st.session_state.importances.head(20), use_container_width=True)

with tab_predict:
    st.header("Previsões")
    if not st.session_state.predictions_made:
        st.info("Faça uma previsão para ver os resultados.")
    else:
        st.dataframe(st.session_state.prediction_df)
        csv_data = convert_df_to_csv(st.session_state.prediction_df)
        st.download_button(
           label="Download CSV",
           data=csv_data,
           file_name='submission.csv',
           mime='text/csv',
        )

with tab_chat:
    st.header("Assistente do Modelo")
    if not st.session_state.model_trained:
        st.info("Treine um modelo para conversar.")
    else:
        for message in st.session_state.chat_messages:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])
        if prompt := st.chat_input("Quais as variáveis mais importantes?"):
            st.session_state.chat_messages.append({"role": "user", "content": prompt})
            response = answer_from_metrics(
                question=prompt,
                task="Regressão",
                metrics_df_or_dict=st.session_state.metrics,
                importances_df=st.session_state.importances
            )
            st.session_state.chat_messages.append({"role": "assistant", "content": response})
            st.rerun()
