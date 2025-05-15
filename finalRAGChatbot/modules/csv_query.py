import pandas as pd
import os

CSV_DIR = "C:/Users/mahmo/OneDrive/Bureau/PIDS_Code/fine_tune"

def load_all_csvs():
    datasets = {}
    for file in os.listdir(CSV_DIR):
        if file.endswith(".csv"):
            key = file.replace("_fine_tune.csv", "")
            df = pd.read_csv(os.path.join(CSV_DIR, file))
            datasets[key] = df
        elif file.endswith(".xlsx"):
            key = file.replace("_fine_tune.xlsx", "")
            df = pd.read_excel(os.path.join(CSV_DIR, file))
            datasets[key] = df
    return datasets

def find_csv_context(datasets, fund_name, category):
    fund_name = fund_name.lower()
    category_map = {
        "team": "team_descriptions",
        "fund": "fund_descriptions",
        "summary": "funds_summaries",
        "funding": "funding_descriptions",
        "avg_rounds": "avg_rounds",
        "country": "country_investments",
        "news": "news_descriptions",
    }

    dataset_key = category_map.get(category.lower())
    if not dataset_key or dataset_key not in datasets:
        return None

    df = datasets[dataset_key]
    matched_rows = df[df.apply(lambda row: fund_name in str(row).lower(), axis=1)]
    if matched_rows.empty:
        return None
    return matched_rows.to_string(index=False)
