
# App AI — integração com OpenAI (tema: Empréstimos e Finanças)
# Objetivo: permitir perguntas e respostas inteligentes sobre crédito e empréstimos.
# Boas práticas:
# - A chave da OpenAI deve ser lida de variável de ambiente ou st.secrets.
# - Nunca deixar a chave em texto no código.
# - Histórico de mensagens mantido no st.session_state.
# - Modelos recomendados: 'gpt-4o-mini' (rápido e econômico) ou 'gpt-4o'.
# - temperature controla criatividade (0 = factual, >0 = mais livre).

import os
import streamlit as st
from openai import OpenAI

st.title("💰 Chat com IA — Consultoria sobre Empréstimos")

def get_api_key():
    # Busca a chave no ambiente ou no secrets do Streamlit
    key = os.getenv('OPENAI_API_KEY')
    if not key:
        try:
            if 'openai_api_key' in st.secrets:
                key = st.secrets['openai_api_key']
        except Exception:
            # st.secrets pode não existir fora do Streamlit
            pass
    return key

def get_client():
    # Valida a chave e cria o cliente da OpenAI
    k = get_api_key()
    if not k:
        st.error("Defina OPENAI_API_KEY ou .streamlit/secrets.toml com openai_api_key.")
        st.stop()
    os.environ['OPENAI_API_KEY'] = k  # garante leitura pelo SDK
    return OpenAI()

# Histórico com mensagem 'system' inicial (define o comportamento da IA)
if 'messages' not in st.session_state:
    st.session_state['messages'] = [{
        'role': 'system',
        'content': (
            'Você é um consultor financeiro especializado em crédito e empréstimos. '
            'Explique conceitos como taxa de juros, parcelas, score de crédito, e risco de inadimplência '
            'de forma clara, educativa e responsável.'
        )
    }]

# Render do histórico (ignora a system)
for m in st.session_state['messages']:
    if m['role'] == 'system':
        continue
    with st.chat_message(m['role']):
        st.write(m['content'])

# Entrada do usuário
msg = st.chat_input('Digite sua dúvida sobre empréstimos, juros ou crédito')

if msg:
    # Registra a mensagem do usuário
    st.session_state['messages'].append({'role': 'user', 'content': msg})
    with st.chat_message('user'):
        st.write(msg)

    # Chamada ao modelo da OpenAI
    try:
        client = get_client()
        resp = client.chat.completions.create(
            model='gpt-4o-mini',  # rápido e com bom custo-benefício
            messages=st.session_state['messages'],  # inclui system + histórico + user
            temperature=0.6,  # equilíbrio entre precisão e naturalidade
        )
        reply = resp.choices[0].message.content
    except Exception as e:
        reply = f'Erro: {e}'

    # Exibe e salva resposta do assistente
    with st.chat_message('assistant'):
        st.write(reply)
    st.session_state['messages'].append({'role': 'assistant', 'content': reply})
