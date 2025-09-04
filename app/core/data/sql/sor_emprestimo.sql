DROP TABLE IF EXISTS sor_emprestimo;

CREATE TABLE sor_emprestimo (
    Loan_ID TEXT,
    Gender TEXT,
    Married TEXT,
    Dependents TEXT,
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
