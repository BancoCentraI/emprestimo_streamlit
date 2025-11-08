
# App AI Step 1 — fluxo de chat com mock (tema: Empréstimos)
# Objetivo: simular o funcionamento de um chat de IA para dúvidas sobre crédito e empréstimos,
# sem precisar de chave da OpenAI nem conexão de rede.
#
# Conceitos:
# - Mensagem 'system': define o comportamento do assistente (a "personalidade" dele).
# - Histórico: armazenado em st.session_state['messages'] como lista de dicionários:
#   {'role': 'system'|'user'|'assistant', 'content': 'texto'}
# - Render: exibe todas as mensagens, exceto a de 'system'.
# - MOCK: gera respostas simuladas para testar o fluxo.

import streamlit as st

st.title("💬 Chat (mock) — Consultoria sobre Empréstimos")

# Inicializa o histórico com uma mensagem 'system' (define o papel da IA)
if 'messages' not in st.session_state:
    st.session_state['messages'] = [{
        'role': 'system',
        'content': 'Você é um consultor financeiro que ajuda usuários a entender empréstimos, juros e crédito pessoal.'
    }]

# Renderiza histórico (ignora a mensagem 'system')
for m in st.session_state['messages']:
    if m['role'] == 'system':
        continue
    with st.chat_message(m['role']):
        st.write(m['content'])

# Campo de entrada do chat
msg = st.chat_input("Digite sua dúvida sobre empréstimos, juros ou crédito")

# Ao enviar, adiciona a mensagem do usuário e gera uma resposta mock
if msg:
    # Adiciona mensagem do usuário ao histórico
    st.session_state['messages'].append({'role': 'user', 'content': msg})
    with st.chat_message('user'):
        st.write(msg)
    # MOCK: resposta simulada (não usa API)
    reply = f"(mock) Analisando sua pergunta sobre empréstimos: '{msg}'. Imagine aqui uma explicação financeira detalhada."
    with st.chat_message('assistant'):
        st.write(reply)
    # Salva a resposta mock no histórico
    st.session_state['messages'].append({'role': 'assistant', 'content': reply})
