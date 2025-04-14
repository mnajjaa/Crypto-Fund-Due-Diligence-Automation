from django.urls import path
from . import views

urlpatterns = [
    path('',views.overview_page, name='overview_page'),
     path('api/coin-list/', views.coin_list_proxy, name='coin_list'),
    path('api/btc-dominance/', views.btc_dominance_proxy, name='btc_dominance'),
    path('firstPageCards', views.firstPageCards, name='firstPageCards'),
    path('api/featured-projects/', views.hotEvents_proxy, name='hotEvents'),
    path('api/topgainers/', views.topgainer_proxy, name='topgainers'),
    path('api/toplosers/', views.toplosers_proxy, name='toplosers'),
    path('api/gainers_loser_24h/', views.gainers_loser_24h, name='gainers_loser_24h'),
    path('api/fundraising-chart/',views.fundraising_chart_proxy, name='fundraising-chart'),
    path('api/ido-chart/',views.ido_chart_proxy, name='ido-chart'),
    path('api/fear_greed/',views.fear_greed, name='fear_greed'),

     path('api/launchpads-roi/', views.launchpads_roi_proxy, name='launchpads_roi'),
    path('api/market-state/', views.market_state_proxy),
    path("api/trending-coins/", views.trending_coins_proxy, name="trending-coins"),
    path("api/recently-listed/", views.recent_coins_proxy, name="recently-listed"),
    path("api/articles/", views.latest_insights, name="latest_insights"),
    path('api/futures-exchange-volumes/', views.fetch_futures_exchange_volumes, name='futures_exchange_volumes'),
    path('api/futures-open-interest/', views.fetch_futures_interest, name='futures_interest'),
    path('api/new-ath/', views.fetch_new_ath, name='new_ath'),
]
