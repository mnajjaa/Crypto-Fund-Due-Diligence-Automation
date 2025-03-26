from django.urls import path
from .views import check_sanctions

urlpatterns = [
    path("check/", check_sanctions, name="check_sanctions"),
]
