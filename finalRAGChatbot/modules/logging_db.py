import sqlite3
from langchain_core.messages import HumanMessage, AIMessage

DB_NAME = "C:/Users/mahmo/OneDrive/Bureau/PIDS_Code/Crypto-Fund-Due-Diligence-Automation/finalRAGChatbot/notebooks/rag_app.db"

def get_db_connection():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    return conn

def create_logs_table():
    conn = get_db_connection()
    conn.execute('''CREATE TABLE IF NOT EXISTS application_logs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        session_id TEXT,
        user_query TEXT,
        gpt_response TEXT,
        model TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)''')
    conn.commit()
    conn.close()

def log_interaction(session_id, question, answer, model="llama3"):
    conn = get_db_connection()
    conn.execute("INSERT INTO application_logs (session_id, user_query, gpt_response, model) VALUES (?, ?, ?, ?)",
                 (session_id, question, answer, model))
    conn.commit()
    conn.close()

def get_chat_history(session_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT user_query, gpt_response FROM application_logs WHERE session_id = ? ORDER BY created_at", (session_id,))
    messages = []
    for row in cursor.fetchall():
        messages.append(HumanMessage(content=row['user_query']))
        messages.append(AIMessage(content=row['gpt_response']))
    conn.close()
    return messages