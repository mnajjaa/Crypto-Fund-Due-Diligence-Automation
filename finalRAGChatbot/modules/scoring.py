def compute_category_score(df, category):
    """
    Compute score for a category using inverse risk_score.
    Assumes risk_score ∈ [0, 10], where 10 is highest risk.
    """
    try:
        return df["risk_score"].apply(lambda x: max(0, 10 - float(x))).mean()
    except:
        return 0

def compute_overall_score(df):
    """
    Aggregate all category scores evenly.
    """
    categories = df["category"].unique()
    if len(categories) == 0:
        return 0
    return sum(compute_category_score(df[df['category'] == cat], cat) for cat in categories) / len(categories)
