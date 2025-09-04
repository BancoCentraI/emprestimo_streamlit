✅ Estratégia de Testes
🔹 Objetivo

Garantir a qualidade e confiabilidade do MVP de concessão de empréstimos, validando tanto os componentes isolados (unitários) quanto o funcionamento integrado do pipeline completo (integração).

🧪 Testes Unitários

Funções utilitárias

infer_cols(df): deve identificar corretamente colunas numéricas e categóricas.

read_csv_smart(path): deve carregar CSVs com diferentes separadores.

Pré-processamento

Pipeline deve imputar valores nulos corretamente (numérico → mediana, categórico → mais frequente).

OneHotEncoder deve lidar com categorias desconhecidas (handle_unknown="ignore").

Modelos

train_classifier: deve retornar pipeline treinado com LogisticRegression.

train_regressor: deve retornar pipeline treinado com LinearRegression.

Métricas

evaluate_classifier: deve retornar dict com accuracy, precision, recall, f1 e matriz de confusão.

evaluate_regressor: deve retornar dict com RMSE.

Explicabilidade

extract_logit_importances: deve retornar DataFrame com coeficientes e odds ratios.

extract_linear_importances: deve retornar DataFrame com pesos ordenados.

🔗 Testes de Integração

Pipeline completo de classificação

Fluxo: dataset → pré-processamento → treino → predição → métricas → importâncias.

Verificar se todas as etapas se conectam sem erros.

Pipeline completo de regressão

Fluxo: dataset → pré-processamento → treino → predição → cálculo de RMSE.

Streamlit App (Smoke Test)

Verificar se a aplicação inicializa (streamlit run app.py) sem exceções.

Inputs de usuário devem retornar outputs do modelo.

⚙️ Ferramentas

Framework de testes: pytest

Cobertura de testes: pytest-cov (opcional)

CI/CD: integração com GitHub Actions (execução automática dos testes a cada push).

📊 Critérios de Aceite

Cobertura mínima de testes unitários: 70%.

Todos os testes de integração devem passar sem falhas.

Aplicação Streamlit deve subir sem erros em ambiente local e no deploy (Smoke Test).