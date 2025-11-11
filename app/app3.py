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

# Tenta importar a OpenAI (opcional)
try:
    from openai import OpenAI
except ImportError:
    OpenAI = None

# --- Configurações da Página ---
st.set_page_config(page_title="Análise de Empréstimo (IA + RAG)", layout="wide")
st.title("💰 Análise de Empréstimo — Pipeline + Chat Inteligente")

# --- Sessão ---
if "model_trained" not in st.session_state:
    st.session_state.model_trained = False
if "predictions_made" not in st.session_state:
    st.session_state.predictions_made = False
if "prediction_df" not in st.session_state:
    st.session_state.prediction_df = None
if "chat_messages" not in st.session_state:
    st.session_state.chat_messages = [{"role": "assistant", "content": "Olá! Treine ou carregue um modelo para começar."}]
if "rag_messages" not in st.session_state:
    st.session_state.rag_messages = []
if "metrics" not in st.session_state:
    st.session_state.metrics = None
if "importances" not in st.session_state:
    st.session_state.importances = None

# --- Diretórios ---
MODEL_DIR = "model"
os.makedirs(MODEL_DIR, exist_ok=True)
MODEL_PATH = os.path.join(MODEL_DIR, "regressor_model.pickle")
IMPUTER_PATH = os.path.join(MODEL_DIR, "num_imputer.pickle")

# --- Funções Auxiliares ---
@st.cache_data
def convert_df_to_csv(df):
    return df.to_csv(index=False).encode('utf-8')

def get_openai_client():
    key = os.getenv("OPENAI_API_KEY")
    if not key or OpenAI is None:
        return None
    try:
        return OpenAI(api_key=key)
    except Exception:
        return None

def build_rag_context(df: pd.DataFrame, max_chars: int = 4000) -> str:
    num_cols = df.select_dtypes(include='number').columns
    cat_cols = df.select_dtypes(include=['object','category','bool']).columns
    parts = [f"Shape: {df.shape[0]} x {df.shape[1]}"]
    if len(num_cols) > 0:
        desc = df[num_cols].describe().T
        desc['median'] = df[num_cols].median()
        cols = ['count','mean','median','std','min','max']
        parts.append("[Resumo Numérico]\n" + desc[cols].to_string())
    if len(cat_cols) > 0:
        cat_summary = []
        for c in cat_cols:
            vc = df[c].value_counts(dropna=False).head(5)
            cat_summary.append(f"{c}:\n{vc.to_string()}")
        parts.append("[Resumo Categórico]\n" + "\n".join(cat_summary))
    ctx = "\n\n".join(parts)
    return ctx[:max_chars] + ("\n... (contexto truncado)" if len(ctx) > max_chars else "")

# --- Layout Lateral ---
with st.sidebar:
    st.header("📂 Upload dos Dados")
    uploaded_files = st.file_uploader(
        "Envie Train.csv (treino) e/ou Test.csv (previsão)",
        type=["csv"],
        accept_multiple_files=True
    )

    st.header("⚙️ Ações do Pipeline")
    test_size = st.slider("Tamanho do conjunto de validação", 0.1, 0.4, 0.2, 0.05)

    # --- Treinar Modelo ---
    if st.button("🚀 Executar Treino"):
        df_train = next((read_csv_smart(f) for f in uploaded_files if "train" in f.name.lower()), None)
        if df_train is not None:
            with st.spinner("Treinando modelo..."):
                create_database_and_tables()
                insert_csv_to_sor(df_train)
                run_etl_sor_to_sot()
                run_etl_sot_to_spec_train()
                df_spec_train = load_data("spec_emprestimo_train")

                target = "Loan_Status"
                y = df_spec_train[target].map({'Y': 1, 'N': 0})
                X = df_spec_train.drop(columns=[target])

                # --- Pré-processamento ---
                num_cols = ['Dependents', 'ApplicantIncome', 'CoapplicantIncome',
                            'LoanAmount', 'Loan_Amount_Term', 'Credit_History']
                X['Dependents'] = X['Dependents'].replace('3+', 3).astype(float)
                X['Credit_History'] = X['Credit_History'].replace({'N': 0, 'Y': 1}).astype(float)

                num_imputer = SimpleImputer(strategy='mean')
                X[num_cols] = num_imputer.fit_transform(X[num_cols])

                pre = make_preprocess_pipeline(X)
                model, X_test, y_test = train_regressor(X, y, pre, test_size=test_size)

                # --- Salva Modelo e Imputador ---
                with open(MODEL_PATH, "wb") as f:
                    pickle.dump(model, f)
                with open(IMPUTER_PATH, "wb") as f:
                    pickle.dump(num_imputer, f)

                # --- Métricas ---
                st.session_state.metrics = evaluate_regressor(model, X_test, y_test)
                st.session_state.importances = extract_linear_importances(model, X.columns, pre)
                st.session_state.model_trained = True
                st.session_state.predictions_made = False

            st.success("✅ Modelo treinado e salvo com sucesso!")
        else:
            st.warning("⚠️ Arquivo 'Train.csv' não encontrado.")

    # --- Fazer Previsão ---
    if st.button("📊 Carregar Modelo e Fazer Previsões"):
        if not os.path.exists(MODEL_PATH) or not os.path.exists(IMPUTER_PATH):
            st.error("Nenhum modelo ou imputador encontrado! Treine primeiro.")
        else:
            df_test = next((read_csv_smart(f) for f in uploaded_files if "test" in f.name.lower()), None)
            if df_test is not None:
                with st.spinner("Gerando previsões..."):
                    run_etl_for_test_data(df_test)
                    df_spec_predict = load_data("spec_emprestimo_predict")

                    with open(IMPUTER_PATH, "rb") as f:
                        num_imputer = pickle.load(f)
                    num_cols = ['Dependents', 'ApplicantIncome', 'CoapplicantIncome',
                                'LoanAmount', 'Loan_Amount_Term', 'Credit_History']

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
                st.success("✅ Previsões geradas com sucesso!")
            else:
                st.warning("⚠️ Arquivo 'Test.csv' não encontrado.")

    # --- Limpar Tudo ---
    if st.button("🧹 Limpar Tudo"):
        drop_database()
        for path in [MODEL_PATH, IMPUTER_PATH]:
            if os.path.exists(path):
                os.remove(path)
        st.session_state.clear()
        st.info("Tudo foi limpo!")
        st.rerun()

# --- Abas ---
tab_train, tab_predict, tab_chat, tab_rag = st.tabs(
    ["📊 Resultados do Treino", "🚀 Previsões", "💬 Chat com o Modelo", "💬 Chat RAG"]
)

# --- Aba Treino ---
with tab_train:
    st.header("📈 Métricas e Importância do Modelo")
    if not st.session_state.model_trained:
        st.info("Treine um modelo para ver os resultados.")
    else:
        st.subheader("📊 Métricas")
        st.json(st.session_state.metrics)
        st.subheader("📌 Importâncias")
        st.dataframe(st.session_state.importances.head(20), use_container_width=True)

# --- Aba Previsão ---
with tab_predict:
    st.header("🚀 Previsões")
    if not st.session_state.predictions_made:
        st.info("Faça uma previsão para ver os resultados.")
    else:
        st.dataframe(st.session_state.prediction_df)
        csv_data = convert_df_to_csv(st.session_state.prediction_df)
        st.download_button("💾 Baixar CSV", csv_data, "submission.csv", "text/csv")

# --- Aba Chat Modelo ---
with tab_chat:
    st.header("🤖 Chat com o Modelo (IA + Métricas)")
    if not st.session_state.model_trained:
        st.info("Treine um modelo para conversar.")
    else:
        for message in st.session_state.chat_messages:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])

        if prompt := st.chat_input("Pergunte algo sobre o modelo ou as variáveis..."):
            st.session_state.chat_messages.append({"role": "user", "content": prompt})
            client = get_openai_client()

            if client:
                try:
                    response = client.chat.completions.create(
                        model="gpt-4o-mini",
                        temperature=0.4,
                        messages=[
                            {"role": "system", "content": "Você é um assistente que explica modelos de previsão de empréstimos."},
                            {"role": "system", "content": f"Métricas: {st.session_state.metrics}\nImportâncias: {st.session_state.importances.head(10).to_dict()}"},
                            {"role": "user", "content": prompt}
                        ]
                    )
                    reply = response.choices[0].message.content
                except Exception as e:
                    reply = f"⚠️ Erro ao acessar OpenAI: {e}"
            else:
                reply = answer_from_metrics(
                    question=prompt,
                    task="Regressão",
                    metrics_df_or_dict=st.session_state.metrics,
                    importances_df=st.session_state.importances
                )

            st.session_state.chat_messages.append({"role": "assistant", "content": reply})
            with st.chat_message("assistant"):
                st.markdown(reply)
            st.rerun()

# --- Aba Chat RAG ---
with tab_rag:
    st.header("🤖 Chat RAG — Perguntas com Contexto da Base")

    # Carrega o dataset base (preferência: Train.csv)
    df_rag = next((read_csv_smart(f) for f in uploaded_files if "train" in f.name.lower()), None)
    if df_rag is None and os.path.exists("emprestimos.csv"):
        df_rag = pd.read_csv("emprestimos.csv")

    if df_rag is None:
        st.info("Faça upload de Train.csv ou coloque emprestimos.csv para usar o chat RAG.")
    else:
        # Parâmetros de exibição
        max_ctx_chars = st.slider("Limite do contexto (caracteres)", 500, 12000, 4000, step=500)
        show_rag_ctx = st.checkbox("Mostrar contexto RAG", value=False)

        # Constrói o contexto (resumo estatístico + amostra de dados)
        rag_context = build_rag_context(df_rag, max_chars=max_ctx_chars)
        if show_rag_ctx:
            with st.expander("📊 Ver contexto RAG (resumo da base)"):
                st.text(rag_context)

        # Inicializa histórico (mantido entre interações)
        if "rag_messages" not in st.session_state:
            st.session_state.rag_messages = [
                {"role": "assistant", "content": "Olá! Eu posso responder perguntas sobre a base de empréstimos com base no contexto gerado."}
            ]

        # Renderiza histórico
        for msg in st.session_state.rag_messages:
            with st.chat_message(msg["role"]):
                st.markdown(msg["content"])

        # Entrada do usuário
        rag_prompt = st.chat_input("Pergunte algo sobre o conjunto de dados ou as variáveis...")

        if rag_prompt:
            # Adiciona mensagem do usuário ao histórico
            st.session_state.rag_messages.append({"role": "user", "content": rag_prompt})

            # Monta as mensagens para o modelo OpenAI
            messages = [
                {"role": "system", "content": "Você é um analista financeiro. Use o contexto fornecido para responder perguntas sobre os dados."},
                {"role": "user", "content": f"Contexto (resumo da base):\n{rag_context}"}
            ]
            # Inclui o histórico (user + assistant)
            for m in st.session_state.rag_messages:
                if m["role"] in ("user", "assistant"):
                    messages.append(m)

            # Faz a chamada à API
            client = get_openai_client()
            if client:
                try:
                    response = client.chat.completions.create(
                        model="gpt-4o-mini",
                        messages=messages,
                        temperature=0.3
                    )
                    reply = response.choices[0].message.content
                except Exception as e:
                    reply = f"⚠️ Erro ao acessar a OpenAI: {e}"
            else:
                # fallback local se não houver OpenAI
                reply = f"(Sem OpenAI configurado)\nPergunta: {rag_prompt}\n\nContexto:\n{rag_context[:1000]}..."

            # Armazena e exibe resposta
            st.session_state.rag_messages.append({"role": "assistant", "content": reply})
            with st.chat_message("assistant"):
                st.markdown(reply)
            st.rerun()
