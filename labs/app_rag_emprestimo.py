
import os
import numpy as np
import pandas as pd
import streamlit as st
from openai import OpenAI

st.set_page_config(page_title="RAG (Resumo Estatístico) — Empréstimos", page_icon="💰")

def get_api_key():
    key = os.getenv('OPENAI_API_KEY')
    if not key:
        try:
            if 'openai_api_key' in st.secrets:
                key = st.secrets['openai_api_key']
        except Exception:
            pass
    return key

def get_client():
    k = get_api_key()
    if not k:
        st.error("Defina OPENAI_API_KEY (ambiente) ou .streamlit/secrets.toml com openai_api_key.")
        st.stop()
    os.environ['OPENAI_API_KEY'] = k
    return OpenAI()

def load_loan_data():
    df = None
    if os.path.exists('emprestimos.csv'):
        try:
            df = pd.read_csv('emprestimos.csv')
        except Exception:
            pass
    if df is None:
        st.error("Coloque um arquivo 'emprestimos.csv' na pasta (com colunas como valor, juros, renda, inadimplente, etc).")
        st.stop()
    return df

def numeric_summary(df: pd.DataFrame) -> str:
    num_cols = df.select_dtypes(include='number').columns
    if len(num_cols) == 0:
        return "(Sem colunas numéricas)"
    desc = df[num_cols].describe().T
    desc['median'] = df[num_cols].median()
    cols = ['count','mean','median','std','min','max']
    return desc[cols].to_string()

def categorical_summary(df: pd.DataFrame) -> str:
    cat_cols = df.select_dtypes(include=['object','category','bool']).columns
    if len(cat_cols) == 0:
        return "(Sem colunas categóricas)"
    lines = []
    for c in cat_cols:
        vc = df[c].value_counts(dropna=False).head(5)
        lines.append(f"Coluna: {c}\n{vc.to_string()}\n")
    return "\n".join(lines)

def correlation_with_default(df: pd.DataFrame) -> str:
    if 'inadimplente' not in df.columns:
        return "(Coluna 'inadimplente' não encontrada)"
    try:
        s = pd.to_numeric(df['inadimplente'], errors='coerce')
        num_cols = df.select_dtypes(include='number').columns
        corrs = []
        for c in num_cols:
            if c == 'inadimplente':
                continue
            corr = s.corr(pd.to_numeric(df[c], errors='coerce'))
            if pd.notna(corr):
                corrs.append((c, corr))
        corrs.sort(key=lambda x: abs(x[1]), reverse=True)
        lines = [f"{c}: {v:.3f}" for c, v in corrs[:10]]
        return "\n".join(lines) if lines else "(Não foi possível calcular correlações)"
    except Exception as e:
        return f"(Erro ao calcular correlações: {e})"

def build_context(df: pd.DataFrame, max_chars: int = 4000) -> str:
    parts = []
    parts.append(f"Shape: {df.shape[0]} linhas x {df.shape[1]} colunas")
    parts.append("\n[Resumo numérico]\n" + numeric_summary(df))
    parts.append("\n[Resumo categórico]\n" + categorical_summary(df))
    parts.append("\n[Correlação com 'inadimplente']\n" + correlation_with_default(df))
    ctx = "\n\n".join(parts)
    if len(ctx) > max_chars:
        ctx = ctx[:max_chars] + "\n... (contexto truncado)"
    return ctx

st.title("RAG (Resumo Estatístico) — Empréstimos")
st.caption("Analisa uma base de empréstimos e gera contexto para perguntas inteligentes com IA.")

with st.sidebar:
    st.header("Configurações")
    max_ctx = st.slider("Limite do contexto (caracteres)", 500, 12000, 4000, step=500)
    show_ctx = st.checkbox("Mostrar contexto gerado", value=False)
    model = st.selectbox("Modelo", ["gpt-4o-mini","gpt-4o","gpt-4.1-mini"], index=0)
    sys_prompt = st.text_area(
        "System prompt",
        value="Você é um analista financeiro. Use o contexto fornecido da base de empréstimos para responder perguntas com precisão e clareza.",
        height=100
    )
    if st.button("Limpar conversa"):
        st.session_state.messages = []

df = load_loan_data()
context_text = build_context(df, max_chars=max_ctx)

if show_ctx:
    with st.expander("Ver contexto (resumo da base)"):
        st.text(context_text)

if 'messages' not in st.session_state or not st.session_state.get('messages'):
    st.session_state.messages = [{'role':'system','content': sys_prompt}]
else:
    if st.session_state.messages[0]['role'] == 'system':
        st.session_state.messages[0]['content'] = sys_prompt

# Render histórico (ignora system)
for m in st.session_state.messages:
    if m['role'] == 'system':
        continue
    with st.chat_message(m['role']):
        st.markdown(m['content'])

prompt = st.chat_input("Pergunte sobre a base de empréstimos")
if prompt:
    st.session_state.messages.append({'role':'user','content': prompt})
    with st.chat_message('user'):
        st.markdown(prompt)
    try:
        client = get_client()
        msgs = st.session_state.messages.copy()
        msgs.insert(1, {'role':'user','content': f"Contexto da base:\n{context_text}"})
        resp = client.chat.completions.create(
            model=model,
            messages=msgs,
            temperature=0.4,
        )
        reply = resp.choices[0].message.content
    except Exception as e:
        reply = f"Erro: {e}"
    with st.chat_message('assistant'):
        st.markdown(reply)
    st.session_state.messages.append({'role':'assistant','content': reply})
