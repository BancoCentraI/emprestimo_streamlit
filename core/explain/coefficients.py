import numpy as np
import pandas as pd

def _feature_names_from_preprocess(pre, original_cols):
    
    pre_step = pre.named_steps["pre"]
    num_cols = pre_step.transformers_[0][2]
    cat_cols = pre_step.transformers_[1][2]

    # Colunas numéricas mantêm o nome original
    out = list(num_cols)

    # Para categóricas, obter nomes expandidos do OneHotEncoder
    ohe = pre_step.named_transformers_["cat"].named_steps["onehot"]
    cat_feature_names = ohe.get_feature_names_out(cat_cols).tolist()

    return out + cat_feature_names


def extract_logit_importances(model_pipe, original_cols, pre):

    clf = model_pipe.named_steps["clf"]
    feature_names = _feature_names_from_preprocess(model_pipe.named_steps["pre"], original_cols)
    coefs = clf.coef_.ravel()
    odds = np.exp(coefs)

    df = pd.DataFrame({
        "feature": feature_names,
        "coef": coefs,
        "odds_ratio": odds
    })
    df["abs_coef"] = df["coef"].abs()

    # Ordena pelo impacto absoluto no risco
    df = df.sort_values("abs_coef", ascending=False).drop(columns="abs_coef")

    # Interpretação amigável para o tema de empréstimos
    df["interpretacao"] = df["coef"].apply(
        lambda x: "↑ Aumenta risco de inadimplência" if x > 0 else "↓ Reduz risco de inadimplência"
    )

    return df


def extract_linear_importances(model_pipe, original_cols, pre):
    
    reg = model_pipe.named_steps["reg"]
    feature_names = _feature_names_from_preprocess(model_pipe.named_steps["pre"], original_cols)
    coefs = reg.coef_.ravel()

    df = pd.DataFrame({
        "feature": feature_names,
        "coef": coefs,
        "abs_coef": np.abs(coefs)
    })

    df = df.sort_values("abs_coef", ascending=False)

    # Interpretação contextualizada para empréstimos
    df["interpretacao"] = df["coef"].apply(
        lambda x: "↑ Eleva o valor do empréstimo/taxa prevista" if x > 0 else "↓ Reduz o valor do empréstimo/taxa prevista"
    )

    return df
