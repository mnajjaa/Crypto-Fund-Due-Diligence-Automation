#ingest.py
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.embeddings import SentenceTransformerEmbeddings
from langchain_community.vectorstores import Chroma
import os

def load_and_split_docs(folder_path="C:/Users/mahmo/OneDrive/Bureau/PIDS_Code/Crypto-Fund-Due-Diligence-Automation/finalRAGChatbot/docs"):
    documents = []
    for file in os.listdir(folder_path):
        if file.endswith(".pdf"):
            loader = PyPDFLoader(os.path.join(folder_path, file))
            documents.extend(loader.load())

    splitter = RecursiveCharacterTextSplitter(chunk_size=300, chunk_overlap=100)
    splits = splitter.split_documents(documents)
    return splits

def create_vectorstore(splits, persist_directory="db"):
    embedding = SentenceTransformerEmbeddings(model_name="all-MiniLM-L6-v2")
    vectorstore = Chroma.from_documents(
        documents=splits,
        embedding=embedding,
        persist_directory=persist_directory,
        collection_name="rag-chatbot"
    )
    return vectorstore