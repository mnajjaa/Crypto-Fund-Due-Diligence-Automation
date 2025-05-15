from django.shortcuts import render

# Create your views here.
from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse, FileResponse, Http404
from django.views.decorators.csrf import csrf_exempt
from .models import UploadedDocument
from django.conf import settings
import os
import os
import uuid
import json
import pandas as pd

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

from finalRAGChatbot.modules.csv_query import load_all_csvs, find_csv_context
from finalRAGChatbot.modules.fund_name_resolver import extract_fund_name_from_question
from finalRAGChatbot.modules.retriever import answer_question
from finalRAGChatbot.modules.ingest import  create_vectorstore
from finalRAGChatbot.modules.retriever import setup_rag_pipeline
from finalRAGChatbot.modules.llm_setup import get_rag_chain

def chatbot_view(request):
    return render(request, 'C:/Users/mahmo/OneDrive/Bureau/PIDS_Code/Crypto-Fund-Due-Diligence-Automation/templates/chatbot/chatbot.html')
@csrf_exempt
def upload_pdf(request):
    if request.method == 'POST' and request.FILES.get('pdf-upload'):
        pdf_file = request.FILES['pdf-upload']
        # Save the uploaded PDF
        document = UploadedDocument(pdf_file=pdf_file)
        document.save()
        # Return the ID of the saved document
        return HttpResponse(str(document.id), status=200)
    return HttpResponse("Invalid request", status=400)


############################################Final Chatbot API############################################
CSV_QUESTIONS_PATH = "C:/Users/mahmo/OneDrive/Bureau/PIDS_Code/Crypto-Fund-Due-Diligence-Automation/funds_treat/notebooks/final_questions_metrics.csv"

def chatbot_interface_view(request):
    df = pd.read_csv(CSV_QUESTIONS_PATH)
    all_categories = df["category"].dropna().unique()

    question_map = {}
    for category in all_categories:
        top_df = get_top_questions_for_category(CSV_QUESTIONS_PATH, category, top_n=5)
        question_map[category] = top_df["question"].tolist()

    return render(request, "C:/Users/mahmo/OneDrive/Bureau/PIDS_Code/Crypto-Fund-Due-Diligence-Automation/templates/chatbot/chatbot_final.html", {
        "categories": list(question_map.keys()),
        "questions_map": question_map
    })
############################################Final Chatbot API end #######################################




def serve_pdf(request, document_id):
    document = get_object_or_404(UploadedDocument, id=document_id)
    response = FileResponse(document.pdf_file, content_type='application/pdf')
    # Set the Content-Disposition header to inline to encourage rendering in the browser
    response['Content-Disposition'] = 'inline; filename="document.pdf"'
    return response

def serve_qa_json(request):
    file_path = os.path.join(settings.BASE_DIR, 'CryptoChatBot', 'Q&A.json')
    if os.path.exists(file_path):
        return FileResponse(open(file_path, 'rb'), content_type='application/json')
    else:
        raise Http404("Q&A.json not found.")
    

########################################################################################################
QUESTIONS_CSV = "C:/Users/mahmo/OneDrive/Bureau/PIDS_Code/Crypto-Fund-Due-Diligence-Automation/funds_treat/notebooks/final_questions_metrics.csv"
OUTPUT_JSON = "output/answered_questions.json"

@csrf_exempt
def generate_due_diligence_answers(request):
    fund_name = request.GET.get("fund", "coinbase ventures").lower()

    # Load vector store (once at app startup ideally)
    splits = load_docs("docs")
    vectorstore = create_vectorstore(splits)
    setup_rag_pipeline(vectorstore)

    # Load CSV + extract top questions
    df = pd.read_csv(QUESTIONS_CSV)

    def compute_priority(row):
        return 2 * row["severity"] + 2 * row["strategic_impact"] + 1.5 * row["category_risk"] - 1.2 * row["data_accessibility"]

    df["priority_score"] = df.apply(compute_priority, axis=1)
    top_questions_df = df.sort_values("priority_score", ascending=False).groupby("category").head(5).reset_index(drop=True)

    # Load context datasets
    datasets = load_all_csvs()
    session_id = str(uuid.uuid4())

    results = []

    for _, row in top_questions_df.iterrows():
        question = row["question"]
        category = row["category"]
        resolved_fund = extract_fund_name_from_question(question) or fund_name
        csv_context = find_csv_context(datasets, resolved_fund, category)

        answer, source = answer_question(
            question=question,
            session_id=session_id,
            fund_name=resolved_fund,
            datasets=datasets,
            category=category,
            metadata=row.to_dict(),
            csv_context=csv_context
        )

        # Heuristics: extract top 3 sentences as key points
        key_points = [s.strip() for s in answer.split(". ") if len(s.strip()) > 20][:3]

        results.append({
            "question": question,
            "category": category,
            "answer": answer,
            "source": source,
            "key_points": key_points
        })

    # Save locally for chatbot reuse
    os.makedirs(os.path.dirname(OUTPUT_JSON), exist_ok=True)
    with open(OUTPUT_JSON, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2)

    return JsonResponse({"session_id": session_id, "fund": fund_name, "results": results}, safe=False)




def get_top_questions_for_category(csv_path: str, category: str, top_n: int = 5) -> pd.DataFrame:
    """
    Load questions from a CSV and return the top N questions for a single specified category.

    Scoring formula:
    - severity (↑ more severe = more important)
    - strategic_impact (↑ more strategic = more important)
    - category_risk (↑ risk = more important)
    - data_accessibility (↓ harder to access = more important)

    Args:
        csv_path (str): Path to the questions CSV.
        category (str): The category to filter on.
        top_n (int): Number of top questions to return.

    Returns:
        pd.DataFrame: Top scored questions for the specified category.
    """
    df = pd.read_csv(csv_path)

    # Filter for the given category only
    df = df[df["category"] == category]

    if df.empty:
        return pd.DataFrame(columns=df.columns)

    def compute_score(row):
        return (
            2 * row["severity"] +
            2 * row["strategic_impact"] +
            1.5 * row["category_risk"] -
            1.2 * row["data_accessibility"]
        )

    df["priority_score"] = df.apply(compute_score, axis=1)

    top_df = df.sort_values("priority_score", ascending=False).head(top_n).reset_index(drop=True)

    return top_df



def get_question_categories(csv_path: str) -> list:
    """
    Load the questions CSV and return a list of unique categories.

    Args:
        csv_path (str): Path to the CSV file containing a 'category' column.

    Returns:
        List[str]: Unique question categories.
    """
    df = pd.read_csv(csv_path)
    return sorted(df["category"].dropna().unique().tolist())



@csrf_exempt
def get_top_questions_api(request):
    """
    API endpoint to return top N questions for a specified category.

    Query Params:
        - category (str): required (e.g., "team")
        - top_n (int): optional (default: 5)

    JSON Response structure:
    {
        "category": "team",
        "top_n": 5,
        "questions": [
            {
                "question": "Who are the key members of the team?",
                "severity": 4,
                "strategic_impact": 5,
                "category_risk": 3,
                "data_accessibility": 2,
                "priority_score": 18.4
            },
            ...
        ]
    }
    """
    category = request.GET.get("category")
    top_n = int(request.GET.get("top_n", 5))
    csv_path = "C:/Users/mahmo/OneDrive/Bureau/PIDS_Code/Crypto-Fund-Due-Diligence-Automation/funds_treat/notebooks/final_questions_metrics.csv"

    if not category:
        return JsonResponse({"error": "Missing 'category' parameter."}, status=400)

    try:
        df = pd.read_csv(csv_path)
        df = df[df["category"] == category]

        if df.empty:
            return JsonResponse({"error": f"No questions found for category '{category}'"}, status=404)

        def compute_score(row):
            return (
                2 * row["severity"] +
                2 * row["strategic_impact"] +
                1.5 * row["category_risk"] -
                1.2 * row["data_accessibility"]
            )

        df["priority_score"] = df.apply(compute_score, axis=1)
        top_df = df.sort_values("priority_score", ascending=False).head(top_n).reset_index(drop=True)

        return JsonResponse({
            "category": category,
            "top_n": top_n,
            "questions": top_df[[
                "question", "severity", "strategic_impact",
                "category_risk", "data_accessibility", "priority_score"
            ]].to_dict(orient="records")
        }, status=200)

    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)



###########################################WebSearch API ##########################################
import os
import trafilatura
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from dotenv import load_dotenv
from exa_py import Exa
import ollama

from finalRAGChatbot.notebooks import sys_msgs  # your custom system prompts

# Load environment variables
load_dotenv(os.path.abspath("finalRAGChatbot/.env"))
EXA_API_KEY = os.getenv("EXA_API_KEY")
if not EXA_API_KEY:
    raise ValueError("EXA_API_KEY not found in environment.")

exa = Exa(EXA_API_KEY)


@csrf_exempt
def web_search_api(request):
    """
    Web search endpoint using LLM + Exa + scraping.

    Query Params:
        - prompt (str): Required user question.

    Returns:
        {
            "prompt": "...",
            "answer": "...",
            "source_link": "...",
            "classification": "short" | "detailed"
        }
    """
    prompt = request.GET.get("prompt")
    if not prompt:
        return JsonResponse({"error": "Missing prompt"}, status=400)

    # Step 1: Generate Search Query
    query_prompt = f'CREATE A SEARCH QUERY FOR THIS PROMPT: \n{prompt}'
    query = ollama.chat(
        model="llama3",
        messages=[
            {'role': 'system', 'content': sys_msgs.query_msg},
            {'role': 'user', 'content': query_prompt}
        ]
    )['message']['content'].strip('"')

    # Step 2: EXA Search (Top 1)
    results = exa.search_and_contents(query=query, num_results=1, text=True, type="auto")
    if not results.results:
        return JsonResponse({"error": "No results from Exa"}, status=404)

    top_result = results.results[0]
    link = top_result.url

    # Step 3: Scrape Content
    scraped = trafilatura.fetch_url(link)
    page_text = trafilatura.extract(scraped, include_formatting=True, include_links=True)

    if not page_text:
        return JsonResponse({"error": "Failed to scrape webpage."}, status=500)

    # Step 4: Classify question type
    classify_prompt = f"### Question to classify:\n{prompt}\n### Classification:"
    classification = ollama.chat(
        model="llama3",
        messages=[{'role': 'user', 'content':  classify_prompt}]
    )['message']['content'].strip().lower()
    classification = "short" if "short" in classification else "detailed"

    # Step 5: Final Prompt + Answer
    if classification == "short":
        final_prompt = (
            f"CONTEXT:\n{page_text}\n\nUSER PROMPT:\n{prompt}\n\n"
            "Answer briefly and strictly based on the context. If unclear, say: "
            "'The information is not available in the provided context.'"
        )
    else:
        final_prompt = (
            f"CONTEXT:\n{page_text}\n\nUSER PROMPT:\n{prompt}\n\n"
            "Answer in detail based only on the context. If unclear, say: "
            "'The information is not available in the provided context.'"
        )

    response = ollama.chat(
        model="llama3",
        messages=[{'role': 'user', 'content': final_prompt}]
    )
    

    return JsonResponse({
        "prompt": prompt,
        "answer": response['message']['content'].strip(),
        "source_link": link,
        "classification": classification
    }, status=200)

##########################################WebSearch API end #######################################

#########################################Answer from CSV API#####################################
# ---------------------------------------------
# 📦 CSV Semantic Search API using FAISS (CPU)
# ---------------------------------------------
import os
import pandas as pd
from typing import List
from langchain_community.vectorstores import FAISS
from langchain_community.embeddings.sentence_transformer import SentenceTransformerEmbeddings
from langchain_core.documents import Document

# ⚙️ Load CSVs into memory
CSV_DIR = "C:/Users/mahmo/OneDrive/Bureau/PIDS_Code/fine_tune"  # Update with your actual directory path
csv_files = [f for f in os.listdir(CSV_DIR) if f.endswith(".csv")]

# 📚 Load CSVs into unified document list
def load_csv_sentences() -> List[Document]:
    all_docs = []
    for file in csv_files:
        df = pd.read_csv(os.path.join(CSV_DIR, file))
        if "sentence" in df.columns and "fund_slug" in df.columns:
            for _, row in df.iterrows():
                metadata = {"source": file, "fund_slug": row.get("fund_slug", "")}
                all_docs.append(Document(page_content=row["sentence"], metadata=metadata))
        elif "description" in df.columns and "fund_slug" in df.columns:
            for _, row in df.iterrows():
                metadata = {"source": file, "fund_slug": row.get("fund_slug", "")}
                all_docs.append(Document(page_content=row["description"], metadata=metadata))
    return all_docs

# 📦 Create or load FAISS vector index
def build_vectorstore(docs: List[Document], persist_path="csv_vector_index"):
    embeddings = SentenceTransformerEmbeddings(model_name="all-MiniLM-L6-v2")
    db = FAISS.from_documents(docs, embeddings)
    db.save_local(persist_path)
    return db

def load_vectorstore(persist_path="csv_vector_index"):
    embeddings = SentenceTransformerEmbeddings(model_name="all-MiniLM-L6-v2")
    return FAISS.load_local(persist_path, embeddings, allow_dangerous_deserialization=True)

# ----------------------------------------
# 🔎 Semantic Search API Entry Function
# ----------------------------------------
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

@csrf_exempt
def search_csv_semantic(request):
    """
    API to perform semantic search in indexed CSV content.

    Query Params:
    - q (str): question or user query (required)
    - short (bool): if true, returns 1–2 matches (default: false)

    Returns:
    {
        "query": "...",
        "results": [
            {"content": "...", "fund_slug": "...", "source": "..."},
            ...
        ]
    }
    """
    query = request.GET.get("q")
    short = request.GET.get("short", "false").lower() == "true"

    if not query:
        return JsonResponse({"error": "Missing query parameter ?q="}, status=400)

    try:
        # Load or initialize the vectorstore
        vectorstore = load_vectorstore()

        # Perform search
        k = 1 if short else 4
        docs = vectorstore.similarity_search(query, k=k)

        results = [{
            "content": doc.page_content,
            "fund_slug": doc.metadata.get("fund_slug", "unknown"),
            "source": doc.metadata.get("source", "csv")
        } for doc in docs]

        return JsonResponse({"query": query, "results": results}, status=200)

    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)

# 🛠️ One-time setup (run from shell or setup view)
# docs = load_csv_sentences()
# build_vectorstore(docs)


#########################################Answer from CSV API end ################################


########################################RAG API#####################################
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from finalRAGChatbot.modules.retriever import answer_question, setup_rag_pipeline
from finalRAGChatbot.modules.ingest import load_and_split_docs, create_vectorstore
from finalRAGChatbot.modules.logging_db import create_logs_table, get_chat_history, log_interaction
import uuid

# Initialize DB + Vectorstore
create_logs_table()
splits = load_and_split_docs("C:/Users/mahmo/OneDrive/Bureau/PIDS_Code/Crypto-Fund-Due-Diligence-Automation/finalRAGChatbot/docs")  # folder with PDFs
vectorstore = create_vectorstore(splits)
setup_rag_pipeline(vectorstore)

@csrf_exempt
def answer_from_rag_only(request):
    """
    API that answers a user question using only the PDF documents (RAG).
    No fallback to web search.

    GET Params:
        - q (str): The user question (required)
        - session (str): Optional session ID (autogenerated if missing)

    Returns:
        {
            "session_id": "...",
            "question": "...",
            "answer": "...",
            "source": "rag" | "no_info"
        }
    """
    question = request.GET.get("q")
    session_id = request.GET.get("session") or str(uuid.uuid4())

    if not question:
        return JsonResponse({"error": "Missing 'q' parameter"}, status=400)

    from finalRAGChatbot.modules.llm_setup import llm_local
    from langchain_core.messages import HumanMessage

    # Override fallback behavior: only RAG
    from finalRAGChatbot.modules.retriever import rag_chain_final, get_chat_history
    chat_history = get_chat_history(session_id)
    result = rag_chain_final.invoke({"input": question, "chat_history": chat_history})
    answer = result.get("answer", "").strip()

    # Detect if nothing was found
    if "The information is not available" in answer:
        return JsonResponse({
            "session_id": session_id,
            "question": question,
            "answer": answer,
            "source": "no_info"
        }, status=200)

    log_interaction(session_id, question, answer, model="llama3")
    return JsonResponse({
        "session_id": session_id,
        "question": question,
        "answer": answer,
        "source": "rag"
    }, status=200)

#######################################RAG API end#####################################
####################################Save history API#####################################

from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
import json
from finalRAGChatbot.utils.qa_history import save_qa_entry

@csrf_exempt
def save_answered_question(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            question = data.get("question")
            answer = data.get("answer")
            fund = data.get("fund")
            source = data.get("source")

            if not all([question, answer, fund, source]):
                return JsonResponse({"error": "Missing fields"}, status=400)

            save_qa_entry(question, answer, fund, source)
            return JsonResponse({"status": "saved"}, status=200)

        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)

    return JsonResponse({"error": "Invalid request method"}, status=405)

####################################end Save history API#####################################