Arquitetura de Software — Loan Prediction Chatbot MVP

Repositório-alvo: kaggle-chatbot-mvp
Tema: Análise de dados de empréstimos financeiros (Kaggle – Loan Prediction)
Objetivo: permitir upload de CSV, treino rápido de modelo (classificação/regressão), explanação de variáveis e chat regrado sobre métricas/coeficientes, tudo via Streamlit.

Visão Geral

O MVP implementa um app Streamlit que orquestra um pipeline simples de ML (scikit-learn) para o dataset de Loan Prediction. O código é organizado por camadas:

UI (app/): interface web (Streamlit) — upload, seleção de tarefa, visualização de métricas/coeficientes e chat.

Core (core/): regras de negócio de dados, pré-processamento, treino, avaliação, explicabilidade e chatbot regrado (sem LLM).

Configs (configs/): configurações (ex.: settings.example.toml, logging.conf).

Dados (data/): CSVs (raw/processed) e modelos treinados (pkl) — apenas no contexto de MVP.

Docs (docs/): documentação técnica e de governança.

Tests (tests/): testes unitários e de integração.

Diagrama de Alto Nível

Fluxo resumido:

Usuário envia train.csv (Loan Prediction) no app.

UI chama Core/Data para leitura robusta (read_csv_smart).

Core/Features cria pipeline de pré-processamento (imputação + one-hot + escala).

Core/Models treina LogisticRegression (alvo Loan_Status) ou LinearRegression (alvo LoanAmount).

Core/Models calcula métricas (acc/prec/rec/f1 + confusão ou RMSE).

Core/Explain extrai coeficientes e efeitos (odds ratio na classificação).

Core/Chatbot formata respostas regradas baseadas em métricas/importâncias.

UI exibe resultados e mantém contexto em st.session_state.

Componentes e Responsabilidades
Camada	Módulo	Responsabilidade	Entradas	Saídas
UI	app/main_app.py	Páginas Streamlit, upload, controles, exibição e chat	CSV, seleção de tarefa	Métricas, tabelas, heatmap, respostas do chat
Dados	core/data/io.py	Leitura robusta de CSV (auto-separador, dtype, encoding)	file_like/path	pd.DataFrame
Features	core/features/preprocess.py	Inferência de colunas num./cat.; imputação; one-hot; escala	X_df	Pipeline de pré-processamento
Modelos	core/models/train.py	Split train/test; treino de Logistic/Linear com Pipeline	X, y, pre	model, X_test, y_test
Modelos	core/models/predict.py	Avaliação (classificação e regressão)	model, X_test, y_test	métricas + matriz de confusão / RMSE
Explicabilidade	core/explain/coefficients.py	Nomes de features pós-one-hot; coeficientes; odds ratio/impacto	model_pipe, pre	DataFrame de importâncias
Chatbot	core/chatbot/rules.py	Respostas regradas a perguntas comuns	pergunta, métricas, importâncias	texto com insights
Fluxo de Dados (End-to-End)

Upload: usuário escolhe arquivo .csv (ex.: train.csv do Kaggle).

Leitura: read_csv_smart tenta separar automaticamente (sep=None, engine='python') e normaliza encoding.

Limpeza de colunas: a UI remove identificadores irrelevantes (ex.: Loan_ID).

Seleção de tarefa:

Classificação: alvo Loan_Status (strings como classes são aceitas pelo scikit-learn).

Regressão: alvo LoanAmount.

Pré-processamento:

Numéricas: SimpleImputer(median) + StandardScaler (dentro de Pipeline).

Categóricas: SimpleImputer(most_frequent) + OneHotEncoder(handle_unknown='ignore').

Treino:

Split train_test_split com test_size configurável.

Classificação → LogisticRegression(max_iter=1000).

Regressão → LinearRegression.

Avaliação:

Classificação → accuracy, precision, recall, f1, matriz de confusão.

Regressão → RMSE.

Explicabilidade:

Classificação → coeficientes da logística + odds ratio.

Regressão → coeficientes e impacto relativo (|coef| × desvio-padrão transformado).

Chat:

Perguntas como “quais variáveis mais importam?” recebem resposta baseada nos top coeficientes.

“métricas/score?” retorna o dicionário de métricas da tarefa atual.

Detalhes Técnicos do Pipeline de ML

Inferência de colunas: infer_cols detecta tipos com df.select_dtypes.

One-Hot: OneHotEncoder(handle_unknown="ignore") evita erros com categorias novas.

Escala: StandardScaler(with_mean=False) quando aplicado após ColumnTransformer esparso; no nosso pré-processamento consolidado, a escala é aplicada dentro do pipeline final de treino.

Labels: Loan_Status pode ser categórico (Y/N). O scikit-learn tratará como classes sem necessidade de mapear para 0/1.

Importâncias:

Logística: coef e odds_ratio = exp(coef). Maiores |coef| indicam maior influência no log-odds.

Linear: ordenação por |coef| e/ou “impacto relativo” para comparar efeitos em diferentes escalas.

Estado, Configuração e Persistência

Estado de sessão: st.session_state guarda last_task, last_metrics, last_importances e histórico do chat.

Configs (opcional no MVP):

configs/settings.example.toml para alvos padrão, tamanho de teste, caminhos de dados.

configs/logging.conf com formato, nível (INFO/DEBUG) e destino (console/arquivo).

Persistência:

MVP: salvar modelos em data/models/ (ex.: loan_logreg.pkl).

Produção: considerar storage externo (S3/GCS) e versionamento de modelos (MLflow/DVC).

Tratamento de Erros e Validações

Leitura de CSV:

Detectar separador automaticamente; se falhar, tentar , e ;.

Mensagens de erro claras no Streamlit (st.error).

Alvo ausente:

Checar presença de Loan_Status (classificação) ou LoanAmount (regressão); interromper com st.stop() se ausente.

Classes insuficientes:

Garantir ao menos duas classes para Loan_Status após limpeza de NAs.

NAs:

Imputação explícita (mediana/mais frequente) para estabilidade do treino.

Matriz de confusão:

Rotulagem defensiva (e.g., “Verdadeiro 0/1”) caso ordem de classes varie.

Segurança, LGPD e Governança (DAMA)

Minimização de dados: use apenas atributos necessários para a predição.

Dados sensíveis: evite coletar; não versionar informações pessoais em git.

Anonimização: datasets do Kaggle já são públicos; ainda assim, não incluir identificadores diretos em exibições.

Logs: sem armazenar dados pessoais; logs limitados a eventos técnicos (erros, shapes, passos do pipeline).

Ciclo de vida: limpeza periódica de data/; README do dataset com metadados (fonte, dicionário de dados).

Acesso: repositório público apenas com exemplos; dados proprietários devem ser externos/privados.

Detalhamento adicional em docs/governance_lgpd.md.

Implantação (Deploy)

Streamlit Cloud:

App: app/main_app.py

Python: 3.11 (ex.: runtime.txt)

Dependências: requirements.txt

Variáveis de ambiente (se usadas): via painel do Streamlit Cloud

Render.com (opcional):

Start Command: streamlit run app/main_app.py --server.port $PORT --server.address 0.0.0.0

Persistência de dados: evitar gravações em disco no dyno (usar storage externo, se necessário)

Guia de publicação em docs/deployment.md.

Testes

Unitários:

core/data/io.py: leitura smart (formas diversas de separador/encoding).

core/features/preprocess.py: fit_transform não deve falhar e manter número esperado de linhas.

core/models/train.py: modelo ajusta sem exceções com um dataset pequeno.

core/models/predict.py: métricas retornam chaves esperadas.

Integração:

Fluxo “CSV → pipeline → métricas/coeficientes”.

Regressão visual (manual):

Conferir que métricas/coeficientes aparecem corretamente no app.

Conferir heatmap da matriz de confusão quando matplotlib estiver instalado.

Estratégia detalhada em docs/testing.md.

Requisitos Não Funcionais

Performance: tempo de treino < 3–5s em datasets de exemplo Kaggle.

Confiabilidade: tratamento de erros de leitura e de colunas ausentes.

Usabilidade: UI clara (duas abas: “Treino & Métricas” e “Chat”).

Portabilidade: execução local (venv) e em nuvem (Streamlit Cloud/Render).

Observabilidade: logs básicos, prints de shapes e parâmetros-chave em DEBUG.

Riscos e Limitações (MVP)

Generalização limitada: modelos simples (Logística/Linear) — sem tuning/validação cruzada.

Explicabilidade linear: coeficientes não capturam relações não lineares/interações.

Dependência do CSV: esquema variável pode exigir ajustes nas colunas descartadas/imputação.

Melhorias Futuras

Validação cruzada + GridSearch/Optuna.

Pipelines por tema com seletores de features (e.g., excluir ApplicantIncome outliers).

Persistência/Versão de modelos (MLflow/DVC).

Autenticação (em produção) e quotas de uso.

SHAP/Permutation Importance para explicabilidade avançada.

Grafos de dependência (Mermaid / Draw.io) e automação de Makefile.

Estrutura de Pastas (Resumo)
kaggle-chatbot-mvp/
├─ app/
│  └─ main_app.py
├─ core/
│  ├─ data/
│  │  └─ io.py
│  ├─ features/
│  │  └─ preprocess.py
│  ├─ models/
│  │  ├─ train.py
│  │  └─ predict.py
│  ├─ explain/
│  │  └─ coefficients.py
│  └─ chatbot/
│     └─ rules.py
├─ configs/
│  ├─ settings.example.toml
│  └─ logging.conf
├─ data/
│  ├─ raw/
│  ├─ processed/
│  └─ models/
├─ docs/
│  ├─ images/architecture.png
│  └─ (demais .md)
├─ tests/
│  └─ (arquivos de teste)
├─ requirements.txt
└─ README.md

Sequência (Mermaid)
sequenceDiagram
  autonumber
  participant U as Usuário
  participant UI as Streamlit UI (app/main_app.py)
  participant IO as Core/Data (io.py)
  participant FE as Core/Features (preprocess.py)
  participant TR as Core/Models (train.py)
  participant PR as Core/Models (predict.py)
  participant EX as Core/Explain (coefficients.py)
  participant CH as Core/Chatbot (rules.py)

  U->>UI: Upload CSV + Seleciona Tarefa
  UI->>IO: read_csv_smart(file)
  IO-->>UI: DataFrame df
  UI->>FE: make_preprocess_pipeline(X)
  FE-->>UI: Pipeline pre
  UI->>TR: train_classifier/regressor(X, y, pre)
  TR-->>UI: model, X_test, y_test
  UI->>PR: evaluate_classifier/regressor(model, X_test, y_test)
  PR-->>UI: métricas (+ matriz de confusão/RMSE)
  UI->>EX: extract_*_importances(model, X.columns, pre)
  EX-->>UI: DataFrame importâncias
  U->>UI: Pergunta no Chat
  UI->>CH: answer_from_metrics(pergunta, task, métricas, importâncias)
  CH-->>UI: Resposta regrada
  UI-->>U: Exibe métricas, importâncias e resposta

Notas para o Diagrama (./docs/images/architecture.png)

Recomenda-se editar em Draw.io/diagrams.net ou Excalidraw e exportar como PNG.

Elementos mínimos:

Camadas: UI (Streamlit) → Core (Data/Features/Models/Explain/Chatbot) → Data (arquivos).

Setas: Upload → Leitura → Pré-processamento → Treino → Avaliação → Explicabilidade → Chat.

Anotações: Tarefa (Classificação/Regressão), Loan_Status/LoanAmount, OneHot+Imputer+Scaler.

Dependências Principais

Core: pandas, numpy, scikit-learn

Visualização: matplotlib, seaborn (opcional)

Web App: streamlit

Testes: pytest

Extra: plotly (opcional)