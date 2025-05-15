# Heuristic approach (you can replace with embedding matching later)

#fetch the knwon funds from this csv file and the funds_details.csv and the column name 
# Path to your CSV
import pandas as pd
csv_path = "C:/Users/mahmo/OneDrive/Bureau/PIDS_Code/Crypto-Fund-Due-Diligence-Automation/funds_treat/notebooks/funds_details.csv"

# Load the CSV file
df = pd.read_csv(csv_path)
KNOWN_FUNDS = df["name"].dropna().unique().tolist()
KNOWN_FUNDS = [f.strip().lower() for f in KNOWN_FUNDS]

def extract_fund_name_from_question(question: str):
    question = question.lower()
    for fund in KNOWN_FUNDS:
        if fund in question:
            return fund
    return None

def extract_fund_name_from_text(text: str):
    text = text.lower()
    for fund in KNOWN_FUNDS:
        if fund in text:
            return fund
    return None
