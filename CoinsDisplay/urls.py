from django.urls import path
from django.conf import settings
from CoinsDisplay import views

urlpatterns = [
    path('coins_view/', views.coins_view, name='coins_view'),
    path('fund_investments/', views.fund_investments, name='fund_investments'),
    path('api/candles/<str:symbol>/', views.get_candles),
    path('api/coin-info/<int:coin_id>/', views.get_coin_info, name='coin_info'),
    path('alerts/', views.fetch_whale_alerts, name='whale-alerts'),
    path('investment-data/', views.fetch_investment_data, name='investment-data'),
    path('fetch-raise-data/', views.fetch_raise_data, name='fetch-raise-data'),
    path('fetch_raise_and_projects_on_blockchains/', views.fetch_raise_and_projects_on_blockchains,name='fetch-raise-and-projects-on-blockchains'),
    path('fetch_token_sales_by_type/', views.fetch_token_sales_by_type, name='fetch-token-sales-by-type'),
]