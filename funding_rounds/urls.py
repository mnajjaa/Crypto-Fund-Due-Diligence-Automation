from django.urls import path
from . import views

urlpatterns = [
    path('', views.funding_dashboard, name='funding_dashboard'),
]
