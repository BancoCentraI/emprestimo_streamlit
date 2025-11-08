
# App AI — Chat com IA (tema: Empréstimos)
# Simples chat de perguntas sobre finanças e crédito usando OpenAI.

import os
import streamlit as st
from openai import OpenAI

st.title("Chat com IA — Análise de Empréstimos 💬")

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
        st.error("Defina OPENAI_API_KEY ou .streamlit/secrets.toml com openai_api_key.")
        st.stop()
    os.environ['OPENAI_API_KEY'] = k
    return OpenAI()

# Histórico com mensagem 'system' inicial
if 'messages' not in st.session_state:
    st.session_state['messages'] = [{
        'role': 'system',
        'content': 'Você é um consultor financeiro especializado em empréstimos e crédito. Responda de forma clara, didática e responsável.'
    }]

# Render histórico (ignora 'system')
for m in st.session_state['messages']:
    if m['role'] == 'system':
        continue
    with st.chat_message(m['role']):
        st.write(m['content'])

# Entrada do usuário
msg = st.chat_input('Digite sua dúvida sobre empréstimos, juros ou crédito pessoal')

if msg:
    st.session_state['messages'].append({'role': 'user', 'content': msg})
    with st.chat_message('user'):
        st.write(msg)
    try:
        client = get_client()
        resp = client.chat.completions.create(
            model='gpt-4o-mini',
            messages=st.session_state['messages'],
            temperature=0.6,
        )
        reply = resp.choices[0].message.content
    except Exception as e:
        reply = f'Erro: {e}'
    with st.chat_message('assistant'):
        st.write(reply)
    st.session_state['messages'].append({'role': 'assistant', 'content': reply})
