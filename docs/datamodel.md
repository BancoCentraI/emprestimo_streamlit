Data Model: Empréstimos

Este documento descreve a modelagem de dados em três camadas: System of Record (SOR), System of Truth (SOT) e Specification (SPEC).

1. System of Record (SOR)

Tabela: sor_emprestimo

Representa os dados brutos, exatamente como chegam do arquivo loan_train.csv. É a primeira camada de armazenamento, garantindo que tenhamos uma cópia fiel dos dados originais.

Propósito: Ingestão e arquivamento dos dados brutos.

Estrutura: As colunas e tipos de dados são uma correspondência direta do CSV. Nenhuma limpeza ou transformação é aplicada aqui.

Coluna	Tipo de Dado (SQL)	Descrição
Loan_ID	TEXT	ID único do empréstimo.
Gender	TEXT	Gênero do solicitante.
Married	TEXT	Estado civil do solicitante.
Dependents	TEXT	Número de dependentes.
Education	TEXT	Escolaridade do solicitante.
Self_Employed	TEXT	Se o solicitante é autônomo.
ApplicantIncome	REAL	Renda mensal do solicitante.
CoapplicantIncome	REAL	Renda mensal do co-solicitante.
LoanAmount	REAL	Valor solicitado do empréstimo.
Loan_Amount_Term	REAL	Prazo do empréstimo (em meses).
Credit_History	REAL	Histórico de crédito (1 = bom, 0 = ruim).
Property_Area	TEXT	Localização do imóvel (Urbana / Semiurbana / Rural).
Loan_Status	TEXT	Variável alvo (Aprovado = Y / Não Aprovado = N).
2. System of Truth (SOT)

Tabela: sot_emprestimo

Esta camada representa a "versão única da verdade". Os dados da SOR são limpos, padronizados e enriquecidos. É a fonte confiável para análises e para a criação de tabelas de features.

Propósito: Fornecer dados limpos e consistentes para a organização.

Transformações Aplicadas:

Tratamento de valores nulos (ex: LoanAmount preenchido com a mediana).

Padronização de valores categóricos (ex: Male/Female → M/F).

Conversão de colunas para tipos adequados (inteiro, real, categórico).

Remoção de identificadores não utilizados na modelagem (ex: Loan_ID).

Coluna	Tipo de Dado (SQL)	Descrição
Gender	TEXT	Gênero do solicitante, padronizado.
Married	TEXT	Estado civil do solicitante.
Dependents	INTEGER	Número de dependentes.
Education	TEXT	Escolaridade.
Self_Employed	TEXT	Se é autônomo.
ApplicantIncome	REAL	Renda mensal do solicitante.
CoapplicantIncome	REAL	Renda mensal do co-solicitante.
LoanAmount	REAL	Valor do empréstimo, com nulos preenchidos.
Loan_Amount_Term	REAL	Prazo do empréstimo, com nulos preenchidos.
Credit_History	REAL	Histórico de crédito.
Property_Area	TEXT	Localização do imóvel.
Loan_Status	TEXT	Variável alvo (Aprovado / Não Aprovado).
3. Specification (SPEC)

Tabela: spec_emprestimo_train

Esta é a tabela final, pronta para ser consumida pelo modelo de machine learning.
Contém as features (variáveis independentes) e a variável alvo.

Propósito: Fornecer um conjunto de dados de treino limpo e pronto para a modelagem.

Estrutura: É essencialmente uma cópia ou visão da SOT, garantindo que o modelo treine com dados da mais alta qualidade.
A separação entre SOT e SPEC permite que, no futuro, possamos criar outras tabelas SPEC para diferentes modelos (ex: spec_credit_score_features) a partir da mesma SOT.

Coluna	Tipo de Dado (SQL)	Descrição
...	...	Todas as colunas da sot_emprestimo.
Loan_Status	TEXT	Variável alvo (Aprovado / Não Aprovado).