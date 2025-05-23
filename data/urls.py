from django.urls import path
from . import views

urlpatterns = [
    path('dashboard/', views.dashboard_view, name='dashboard'),
    path('project/<str:symbol>/', views.project_data, name='project_data'),
    path('watchlist/add/<str:symbol>/', views.add_to_watchlist, name='add_to_watchlist'),
    path('dashFunds/',views.dashFunds, name='dashFunds'),
    path('fund/<slug:slug>/', views.single_fund_view, name='single_fund'),
    path('focus-area/<slug:slug>/', views.focus_area_view, name='focus-area'),
]
