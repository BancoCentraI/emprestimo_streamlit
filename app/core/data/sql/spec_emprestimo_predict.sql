-- Remove a tabela antiga se existir
DROP TABLE IF EXISTS spec_emprestimo_predict;

-- Cria a tabela para predição
CREATE TABLE spec_emprestimo_predict (
    Loan_ID TEXT,
    Gender TEXT,
    Married TEXT,
    Dependents TEXT,       -- Dependents como TEXT para suportar "3+"
    Education TEXT,
    Self_Employed TEXT,
    ApplicantIncome REAL,
    CoapplicantIncome REAL,
    LoanAmount REAL,
    Loan_Amount_Term REAL,
    Credit_History REAL,
    Property_Area TEXT
);
