from django.urls import path
from . import views

urlpatterns = [
    path('', views.pptx_view, name='pptx_view'),
    
]