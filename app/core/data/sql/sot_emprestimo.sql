DROP TABLE IF EXISTS sot_emprestimo;

CREATE TABLE sot_emprestimo (
    Gender TEXT,
    Married TEXT,
    Dependents TEXT,       -- Ajustado para suportar "3+"
    Education TEXT,
    Self_Employed TEXT,
    ApplicantIncome REAL,
    CoapplicantIncome REAL,
    LoanAmount REAL,
    Loan_Amount_Term REAL,
    Credit_History REAL,
    Property_Area TEXT,
    Loan_Status TEXT
);
