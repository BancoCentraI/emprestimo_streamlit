import sqlite3
import pandas as pd
import os

# Pega o caminho absoluto do diretório onde este arquivo (database.py) está.
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
SQL_DIR = os.path.join(CURRENT_DIR, "sql")
APP_DIR = os.path.dirname(os.path.dirname(CURRENT_DIR))
DB_NAME = os.path.join(APP_DIR, "emprestimo.db")  # <-- ALTERADO

def connect_db():
    """Cria uma conexão com o banco de dados SQLite."""
    return sqlite3.connect(DB_NAME)

def execute_sql_from_file(filepath):
    """Lê um arquivo .sql e executa os comandos."""
    conn = connect_db()
    cursor = conn.cursor()
    with open(filepath, 'r') as f:
        sql_script = f.read()
    cursor.executescript(sql_script)
    conn.commit()
    conn.close()

def create_database_and_tables():
    """Cria o banco de dados e todas as tabelas a partir dos arquivos .sql."""
    if os.path.exists(DB_NAME):
        os.remove(DB_NAME)
    
    sql_files = [
        os.path.join(SQL_DIR, "sor_emprestimo.sql"),       # <-- ALTERADO
        os.path.join(SQL_DIR, "sot_emprestimo.sql"),       # <-- ALTERADO
        os.path.join(SQL_DIR, "spec_emprestimo_train.sql"),# <-- ALTERADO
        os.path.join(SQL_DIR, "spec_emprestimo_predict.sql") # <-- ALTERADO
    ]
    for filepath in sql_files:
        if not os.path.exists(filepath):
            raise FileNotFoundError(f"Arquivo SQL não encontrado: {filepath}")
        execute_sql_from_file(filepath)
    print("Banco de dados e tabelas criados com sucesso.")

def insert_csv_to_sor(df):
    """Insere os dados de um DataFrame na tabela SOR."""
    conn = connect_db()
    # A tabela SOR é genérica, então apenas inserimos os dados de treino nela
    df_train = df[df['Loan_Status'].notna()]  # <-- ALTERADO
    df_train.to_sql("sor_emprestimo", conn, if_exists="replace", index=False)  # <-- ALTERADO
    conn.close()
    print("Dados de treino inseridos na tabela SOR.")

def run_etl_sor_to_sot():
    """Executa a transformação de SOR para SOT para os dados de treino."""
    conn = connect_db()
    df = pd.read_sql_query("SELECT * FROM sor_emprestimo", conn)  # <-- ALTERADO

    # Lógica de Transformação (ajustada para empréstimo)
    df['LoanAmount'].fillna(df['LoanAmount'].median(), inplace=True)
    df['Loan_Amount_Term'].fillna(df['Loan_Amount_Term'].mode()[0], inplace=True)
    df['Credit_History'].fillna(df['Credit_History'].mode()[0], inplace=True)

    # Padronização de categorias
    df['Gender'] = df['Gender'].replace({'Male': 'M', 'Female': 'F'})
    df['Married'] = df['Married'].replace({'Yes': 'Y', 'No': 'N'})

    # Inserir na SOT (sem Loan_ID)
    df_sot = df.drop(columns=['Loan_ID'], errors='ignore')
    df_sot.to_sql("sot_emprestimo", conn, if_exists="replace", index=False)  # <-- ALTERADO
    conn.close()
    print("ETL de SOR para SOT (treino) concluído.")

def run_etl_sot_to_spec_train():
    """Copia dados da SOT para a SPEC de treino."""
    conn = connect_db()
    df = pd.read_sql_query("SELECT * FROM sot_emprestimo", conn)  # <-- ALTERADO
    df.to_sql("spec_emprestimo_train", conn, if_exists="replace", index=False)  # <-- ALTERADO
    conn.close()
    print("ETL de SOT para SPEC (treino) concluído.")

def run_etl_for_test_data(df_test):
    """Executa o ETL para os dados de teste e salva na SPEC de previsão."""
    conn = connect_db()
    
    # Aplica as mesmas transformações dos dados de treino
    df_test['LoanAmount'].fillna(df_test['LoanAmount'].median(), inplace=True)
    df_test['Loan_Amount_Term'].fillna(df_test['Loan_Amount_Term'].mode()[0], inplace=True)
    df_test['Credit_History'].fillna(df_test['Credit_History'].mode()[0], inplace=True)

    df_test['Gender'] = df_test['Gender'].replace({'Male': 'M', 'Female': 'F'})
    df_test['Married'] = df_test['Married'].replace({'Yes': 'Y', 'No': 'N'})
    
    # Mantém os identificadores para o resultado final
    df_spec = df_test[['Loan_ID'] + [col for col in df_test.columns if col != 'Loan_ID']]
    
    df_spec.to_sql("spec_emprestimo_predict", conn, if_exists="replace", index=False)  # <-- ALTERADO
    conn.close()
    print("ETL para dados de teste concluído e salvo na SPEC (previsão).")

def load_data(table_name: str):
    """Carrega dados de qualquer tabela especificada."""
    conn = connect_db()
    df = pd.read_sql_query(f"SELECT * FROM {table_name}", conn)
    conn.close()
    return df

def drop_database():
    """Remove o arquivo do banco de dados."""
    if os.path.exists(DB_NAME):
        os.remove(DB_NAME)
        print(f"Banco de dados '{DB_NAME}' removido.")
