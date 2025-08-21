import numpy as np
import pandas as pd
from sklearn.pipeline import Pipeline
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.impute import SimpleImputer

def infer_cols(df: pd.DataFrame):
    
    num_cols = df.select_dtypes(include=[np.number]).columns.tolist()
    cat_cols = [c for c in df.columns if c not in num_cols]
    return num_cols, cat_cols


def make_preprocess_pipeline(X_df: pd.DataFrame) -> Pipeline:
   
    num_cols, cat_cols = infer_cols(X_df)

    # Pipeline para variáveis numéricas
    num_pipe = Pipeline(steps=[
        ("impute", SimpleImputer(strategy="median")),
        ("scale", StandardScaler())   # normaliza distribuição
    ])

    # Pipeline para variáveis categóricas
    cat_pipe = Pipeline(steps=[
        ("impute", SimpleImputer(strategy="most_frequent")),
        ("onehot", OneHotEncoder(handle_unknown="ignore", sparse_output=False))
    ])

    # Combinação em um ColumnTransformer
    pre = ColumnTransformer(transformers=[
        ("num", num_pipe, num_cols),
        ("cat", cat_pipe, cat_cols)
    ])

    # Retorna um pipeline completo de pré-processamento
    return Pipeline([("pre", pre)])
