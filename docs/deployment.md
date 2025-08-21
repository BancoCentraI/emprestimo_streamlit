🚀 Deploy da Aplicação

Este guia mostra como publicar o projeto de Previsão de Empréstimos em duas opções de PaaS: Streamlit Cloud e Render.

📌 Pré-requisitos

Conta no GitHub
 (código versionado no repositório).

Arquivo requirements.txt atualizado (já configurado).

Repositório público ou privado (neste caso, dar acesso à plataforma escolhida).

🌐 Opção 1: Deploy no Streamlit Cloud

Acesse: https://streamlit.io/cloud
.

Faça login com sua conta do GitHub.

Clique em "New app".

Selecione o repositório onde está o projeto.

Configure:

Branch: main (ou outra branch principal).

Main file path: app/streamlit_app.py (ou o script principal da aplicação).

Clique em Deploy.

Após alguns minutos, a aplicação ficará disponível em um link do tipo:

https://seu-usuario-seu-repo.streamlit.app


🔧 Dicas:

Se atualizar o código no GitHub, o Streamlit Cloud automaticamente redeploya.

Use um arquivo secrets.toml no painel do Streamlit Cloud para variáveis sensíveis (ex.: chaves de API).

☁️ Opção 2: Deploy no Render

Acesse https://render.com
 e crie uma conta.

Clique em New > Web Service.

Conecte seu GitHub e selecione o repositório.

Configure:

Environment: Python 3.x

Build Command:

pip install -r requirements.txt


Start Command:

streamlit run app/streamlit_app.py --server.port $PORT --server.address 0.0.0.0


Escolha a instância gratuita (Free Tier) ou paga.

Clique em Create Web Service.

🔧 Dicas:

No Render, o app terá URL do tipo:

https://nome-do-app.onrender.com


Lembre de expor a porta com a variável $PORT.

📊 Comparação rápida
Plataforma	Vantagem	Limitação
Streamlit Cloud	Simplicidade, auto-redeploy, focado em apps Streamlit	Menos customização
Render	Mais flexível, suporta múltiplos serviços (API + frontend)	Configuração inicial mais complexa