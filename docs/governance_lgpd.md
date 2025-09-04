🛡️ Governança e LGPD

Este documento apresenta as diretrizes de governança de dados e os princípios da LGPD (Lei Geral de Proteção de Dados - Lei nº 13.709/2018) aplicados neste projeto de previsão de empréstimos.

📑 Princípios de Governança de Dados

Transparência – todos os fluxos de tratamento de dados são documentados.

Qualidade dos Dados – foco na consistência, acurácia e completude dos dados utilizados para o modelo.

Segurança – aplicação de boas práticas de proteção contra acessos não autorizados.

Minimização – apenas os atributos necessários para a análise são coletados e processados.

Accountability (Prestação de Contas) – logs e documentação garantem a rastreabilidade das decisões do modelo.

⚖️ Princípios da LGPD aplicados

Finalidade

Os dados são utilizados exclusivamente para análise e modelagem preditiva de empréstimos, sem reuso indevido.

Adequação

O tratamento está compatível com a finalidade explícita e legítima do projeto.

Necessidade

Apenas dados mínimos essenciais foram considerados para a predição (ex.: renda, histórico de crédito, valor solicitado).

Livre acesso

O usuário/cliente tem direito de saber quais informações foram usadas e como influenciam a decisão.

Qualidade dos dados

Rotinas de limpeza e imputação asseguram consistência antes do treinamento do modelo.

Transparência

Documentação sobre como os modelos foram treinados e quais variáveis mais influenciam está disponível.

Segurança

Dados sensíveis não foram utilizados no MVP. Em produção, seriam criptografados e acessados apenas com controle de permissões.

Prevenção

Testes de fairness e explicabilidade podem ser adicionados para evitar discriminação algorítmica.

Não discriminação

O modelo não utiliza atributos diretamente relacionados a raça, religião, gênero ou outros dados sensíveis.

Responsabilização e prestação de contas

O projeto mantém registro das decisões técnicas, pipelines e métricas de desempenho do modelo.

🔐 Boas práticas adicionais

Versionamento do código no GitHub.

Uso de ambientes controlados (conda/venv).

Logs de execução e auditoria do modelo.

Possibilidade de implementar explainability (XAI) para justificar decisões individuais.