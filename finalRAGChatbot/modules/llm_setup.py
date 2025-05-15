
#llm_setup.py
from langchain_ollama import OllamaLLM
from langchain.chains import create_history_aware_retriever, create_retrieval_chain
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder

llm_local = OllamaLLM(model="llama3", base_url="http://localhost:11434")

qa_prompt = ChatPromptTemplate.from_messages([
    ("system", "You are an intelligent assistant specializing in crypto whitepapers. Use only the provided context. If uncertain, respond: 'The information is not available in the document.'"),
    ("system", "Context: {context}"),
    MessagesPlaceholder(variable_name="chat_history"),
    ("human", "{input}")
])

contextualize_q_prompt = ChatPromptTemplate.from_messages([
    ("system", "Reformulate the user’s question to be self-contained."),
    MessagesPlaceholder("chat_history"),
    ("human", "{input}")
])

def get_rag_chain(vectorstore):
    retriever = vectorstore.as_retriever(search_kwargs={"k": 3})
    history_aware_retriever = create_history_aware_retriever(llm_local, retriever, contextualize_q_prompt)
    question_answer_chain = create_stuff_documents_chain(llm_local, qa_prompt)
    return create_retrieval_chain(history_aware_retriever, question_answer_chain)