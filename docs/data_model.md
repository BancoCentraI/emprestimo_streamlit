📑 Modelagem de Dados
1. Diagrama Entidade-Relacionamento (DER)

O conjunto de dados do Loan Prediction possui uma estrutura relativamente simples: uma tabela principal representando Solicitações de Empréstimo, com atributos de clientes e do próprio empréstimo.

Entidades principais:

Cliente

Identificado indiretamente via Loan_ID.

Atributos: Gender, Married, Dependents, Education, Self_Employed.

Empréstimo

Representa o pedido de crédito.

Atributos: LoanAmount, Loan_Amount_Term, Credit_History, Property_Area, Loan_Status.

Relacionamento:

Cliente (1) —— (1) Empréstimo

Cada cliente está vinculado a um único pedido de empréstimo (neste dataset).

Em uma aplicação real, poderíamos modelar como (1-N), já que um cliente poderia solicitar vários empréstimos.

2. Dicionário de Dados
Coluna	Tipo de dado	Descrição
Loan_ID	string	Identificador único do pedido de empréstimo.
Gender	categórico	Gênero do solicitante (Male, Female).
Married	categórico	Estado civil (Yes, No).
Dependents	categórico	Número de dependentes (0, 1, 2, 3+).
Education	categórico	Escolaridade (Graduate, Not Graduate).
Self_Employed	categórico	Se é autônomo (Yes, No).
ApplicantIncome	numérico	Renda do solicitante.
CoapplicantIncome	numérico	Renda do co-solicitante (se houver).
LoanAmount	numérico	Valor do empréstimo solicitado (em milhares).
Loan_Amount_Term	numérico	Prazo do empréstimo (em meses).
Credit_History	binário	Histórico de crédito (1 = bom, 0 = ruim).
Property_Area	categórico	Área do imóvel (Urban, Semiurban, Rural).
Loan_Status	binário (target)	Status do empréstimo (Y = aprovado, N = negado).