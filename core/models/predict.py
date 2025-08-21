from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    confusion_matrix,
    roc_auc_score,
    roc_curve,
    mean_squared_error,
    mean_absolute_error,
    r2_score,
)
import numpy as np

def evaluate_classifier(model, X_test, y_test):

    y_pred = model.predict(X_test)

    # Detecta se os labels são strings
    if y_test.dtype == object or isinstance(y_test.iloc[0], str):
        pos_label = 'Y'  # considere 'Y' como classe positiva
    else:
        pos_label = 1

    # Tenta obter probabilidades se o modelo suportar
    y_proba = None
    try:
        y_proba = model.predict_proba(X_test)
        # Se coluna alvo for string, pega a coluna correspondente a pos_label
        if y_proba.shape[1] == 2 and isinstance(pos_label, str):
            classes = model.classes_
            y_proba = y_proba[:, list(classes).index(pos_label)]
        else:
            y_proba = y_proba[:, 1]
    except Exception:
        y_proba = None

    metrics = {
        "accuracy": float(accuracy_score(y_test, y_pred)),
        "precision": float(precision_score(y_test, y_pred, pos_label=pos_label, zero_division=0)),
        "recall": float(recall_score(y_test, y_pred, pos_label=pos_label, zero_division=0)),
        "f1": float(f1_score(y_test, y_pred, pos_label=pos_label, zero_division=0)),
    }

    # Adiciona AUC-ROC se possível
    if y_proba is not None:
        try:
            metrics["auc_roc"] = float(roc_auc_score(y_test.map({pos_label:1, **{l:0 for l in y_test.unique() if l!=pos_label}}), y_proba))
        except Exception:
            pass

    cm = confusion_matrix(y_test, y_pred, labels=[l for l in sorted(y_test.unique())]).tolist()
    return metrics, cm


def evaluate_regressor(model, X_test, y_test):

    y_pred = model.predict(X_test)

    rmse = float(np.sqrt(mean_squared_error(y_test, y_pred)))
    mae = float(mean_absolute_error(y_test, y_pred))
    r2 = float(r2_score(y_test, y_pred))

    return {"rmse": rmse, "mae": mae, "r2": r2}
