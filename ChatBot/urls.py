# from django.contrib import admin
from django.urls import path
from django.conf import settings
from ChatBot import views
urlpatterns = [
    path('chatbot/', views.chatbot_view, name='chatbot'),
    path('upload_pdf/', views.upload_pdf, name='upload_pdf'),
    path('serve_pdf/<int:document_id>/', views.serve_pdf, name='serve_pdf'),
    ]