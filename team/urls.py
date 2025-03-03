from django.urls import path
from .views import upload_document, extract_team

urlpatterns = [
    path('upload/', upload_document, name='upload_document'),  
    path('extract_team/', extract_team, name='extract_team'),
]
