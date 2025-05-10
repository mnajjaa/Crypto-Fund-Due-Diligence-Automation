from django.urls import path
from django.conf import settings
from CoinsDisplay import views

urlpatterns = [
    path('coins_view/', views.coins_view, name='coins_view'),
    path('api/candles/<str:symbol>/', views.get_candles),
    path('api/coin-info/<int:coin_id>/', views.get_coin_info, name='coin_info'),
    path('alerts/', views.fetch_whale_alerts, name='whale-alerts'),
]