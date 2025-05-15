#retriever.py
from .llm_setup import llm_local, get_rag_chain
from .logging_db import get_chat_history
from finalRAGChatbot.notebooks.test import main as web_search_fallback

vectorstore = None  # should be initialized in a setup script
rag_chain_final = None

def setup_rag_pipeline(vstore):
    global vectorstore, rag_chain_final
    vectorstore = vstore
    rag_chain_final = get_rag_chain(vectorstore)

def answer_question(question, session_id):
    chat_history = get_chat_history(session_id)
    result = rag_chain_final.invoke({"input": question, "chat_history": chat_history})

    if "The information is not available" not in result['answer']:
        return result['answer'], "rag"

    return web_search_fallback(question), "web"

#from .llm_setup import llm_local, get_rag_chain
#from .logging_db import get_chat_history
#from notebooks.test import main as web_search_fallback
#from langchain_core.messages import HumanMessage
#
#vectorstore = None
#rag_chain_final = None
#
#def setup_rag_pipeline(vstore):
#    global vectorstore, rag_chain_final
#    vectorstore = vstore
#    rag_chain_final = get_rag_chain(vectorstore)
#
#def answer_question(
#    question: str,
#    session_id: str,
#    fund_name: str,
#    datasets: dict,
#    category: str,
#    metadata: dict = None,
#    csv_context: str = None
#) -> tuple[str, str]:
#    """
#    Answer the question using RAG first. If no info found, fallback to web search + CSV context.
#    """
#    chat_history = get_chat_history(session_id)
#
#    # Step 1: Try RAG first
#    result = rag_chain_final.invoke({"input": question, "chat_history": chat_history})
#    if "The information is not available" not in result['answer']:
#        return result['answer'], "rag"
#
#    # Step 2: Web fallback
#    web_result = web_search_fallback(question)
#
#    # Step 3: Merge CSV and Web context
#    combined_context = ""
#    if csv_context:
#        combined_context += f"📄 CSV Context:\n{csv_context}\n\n"
#    if web_result:
#        combined_context += f"🌐 Web Context:\n{web_result}\n\n"
#
#    # Final prompt to LLM
#    final_prompt = (
#        f"As a due diligence analyst, answer the following question using only the context provided.\n\n"
#        f"{combined_context}"
#        f"Question: {question}"
#    )
#
#    try:
#        response = llm_local.invoke([HumanMessage(content=final_prompt)])
#        return response.content.strip(), "web+csv"
#    except Exception as e:
#        return f"Error during LLM invocation: {str(e)}", "error"
