

def answer_from_metrics(question: str, task: str, metrics_df_or_dict, importances_df):
    """
    Responde perguntas do usuário com base nas métricas do modelo,
    importâncias de variáveis e contexto do pipeline.

    Args:
        question (str): Pergunta do usuário em linguagem natural.
        task (str): Tipo de tarefa ("classificação" ou "regressão").
        metrics_df_or_dict: Métricas calculadas (dict ou DataFrame).
        importances_df: DataFrame com variáveis e seus pesos/coeficientes.

    Returns:
        str: Resposta em linguagem natural para o usuário.
    """
    q = (question or "").lower()

    # Variáveis mais importantes
    if "importan" in q or "importân" in q or "variáve" in q or "features" in q:
        top_vars = importances_df.head(5)[["feature"]].to_dict("records")
        top_str = ", ".join([t["feature"] for t in top_vars])
        return (
            f"As variáveis mais influentes para aprovação de empréstimos são: {top_str}. "
            "Essas variáveis têm maior peso no cálculo da probabilidade de um cliente ser aprovado. "
            "A interpretação é feita a partir dos coeficientes e odds ratio do modelo."
        )

    # Métricas do modelo
    if "métric" in q or "score" in q or "acur" in q or "rmse" in q or "precisão" in q or "desempenho" in q:
        return (
            f"O desempenho do modelo na tarefa **{task}** foi avaliado com as seguintes métricas: "
            f"{metrics_df_or_dict}. "
            "Esses valores ajudam a entender a qualidade das previsões e a confiabilidade do modelo."
        )

    # Como foi treinado
    if "como foi treinado" in q or "pipeline" in q or "processo" in q:
        return (
            "O pipeline de treino para análise de empréstimos funciona assim:\n"
            "- Tratamento de valores ausentes (imputação por mediana ou moda);\n"
            "- Codificação one-hot para variáveis categóricas (como estado civil, tipo de imóvel, histórico de crédito);\n"
            "- Padronização das variáveis numéricas (como renda e valor do empréstimo);\n"
            "- Treinamento de **Regressão Logística** (para prever se o empréstimo será aprovado ou não — variável `Loan_Status`);\n"
            "- Ou treinamento de **Regressão Linear** (para prever valores contínuos, como o montante do empréstimo)."
        )

    # Privacidade e LGPD
    if "privacid" in q or "lgpd" in q or "dados pessoais" in q:
        return (
            "Neste MVP, não utilizamos dados pessoais identificáveis — todos os registros são anonimizados. "
            "Os dados usados servem apenas para fins de estudo. "
            "Para um sistema em produção, seria necessário aplicar medidas da **LGPD**, incluindo:\n"
            "- Consentimento explícito do cliente;\n"
            "- Minimização do uso de dados (apenas o necessário para a análise);\n"
            "- Anonimização sempre que possível;\n"
            "- Auditoria e rastreabilidade do uso das informações."
        )

    # Resposta padrão
    return (
        "Posso responder perguntas sobre: variáveis que mais impactam a aprovação de crédito, "
        "métricas de desempenho do modelo ou como funciona o pipeline de treino.\n"
        "Exemplo: 'Quais variáveis mais importam para aprovar um empréstimo?'"
    )
