from django.urls import path
import finalRAGChatbot.views as views

urlpatterns = [
    path("api/websearch", views.web_search_api, name="web_search_api"),
    path("api/search-csv", views.search_csv_semantic, name="search_csv_semantic"),
    path("api/rag-answer", views.answer_from_rag_only, name="rag_answer_api"),
    path("chatbot/", views.chatbot_interface_view, name="chatbot"),
    path("api/save-qa", views.save_answered_question, name="save_answered_question"),

]
