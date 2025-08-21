import pandas as pd
import io
import os
import streamlit as st  # necessário para mostrar no app

def read_csv_smart(file_or_path, expected_sep=None):
    # Se for caminho local (string)
    if isinstance(file_or_path, str) and os.path.exists(file_or_path):
        df = pd.read_csv(file_or_path, sep=expected_sep, engine="python", encoding="utf-8", on_bad_lines="skip")

    # Se for upload via Streamlit (BytesIO ou Similar)
    elif hasattr(file_or_path, "read"):
        # reset ponteiro
        file_or_path.seek(0)
        try:
            df = pd.read_csv(file_or_path, sep=expected_sep, engine="python", encoding="utf-8", on_bad_lines="skip")
        except UnicodeDecodeError:
            file_or_path.seek(0)
            df = pd.read_csv(file_or_path, sep=expected_sep, engine="python", encoding="latin-1", on_bad_lines="skip")

    else:
        raise ValueError("Entrada inválida para read_csv_smart: forneça um caminho válido ou objeto de upload.")

    # Normalizar nomes das colunas
    df.columns = [c.strip() for c in df.columns]

    # Mostrar as colunas carregadas (para debug)
    st.write("Colunas disponíveis no CSV:", df.columns.tolist())

    # Converter IDs para string (se existirem)
    for col in df.columns:
        if "id" in col.lower():
            df[col] = df[col].astype(str)

    return df
