import os
import json
from datetime import datetime

QA_PATH = os.path.join(
    os.path.dirname(__file__),
    "../output/answered_questions.json"
)

def load_qa_history():
    if not os.path.exists(QA_PATH):
        return []
    with open(QA_PATH, "r", encoding="utf-8") as f:
        try:
            return json.load(f)
        except json.JSONDecodeError:
            return []

def save_qa_entry(question, answer, fund, source):
    data = load_qa_history()
    entry = {
        "question": question,
        "answer": answer,
        "fund": fund,
        "source": source,
        "timestamp": datetime.utcnow().isoformat()
    }
    data.append(entry)
    with open(QA_PATH, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

def get_context_for_fund(fund):
    data = load_qa_history()
    return [f"Q: {e['question']} | A: {e['answer']}" for e in data if e.get("fund") == fund]


def load_previous_answers(fund_name, max_entries=5):
    if not os.path.exists(QA_PATH):
        return []

    with open(QA_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)

    # Filter by fund name
    fund_entries = [entry for entry in data if entry["fund"] == fund_name]

    # Return latest N entries
    return fund_entries[-max_entries:]