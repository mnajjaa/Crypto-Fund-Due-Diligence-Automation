"""
URL configuration for duedeals project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from . import views  # Add this line


urlpatterns = [
    path('admin/', admin.site.urls),
    path('firstPage',views.firstPage, name='firstPage'),
    path('api/coin-list/', views.coin_list_proxy, name='coin_list'),
    path('api/btc-dominance/', views.btc_dominance_proxy, name='btc_dominance'),
    path('firstPageCards', views.firstPageCards, name='firstPageCards'),
    path('api/featured-projects/', views.hotEvents_proxy, name='hotEvents'),
    path('api/topgainers/', views.topgainer_proxy, name='topgainers'),
    path('api/toplosers/', views.toplosers_proxy, name='toplosers'),
    path('api/gainers_loser_24h/', views.gainers_loser_24h, name='gainers_loser_24h'),
    path('api/launchpads-roi/', views.launchpads_roi_proxy, name='launchpads_roi'),
    path('api/market-state/', views.market_state_proxy),
    path("api/trending-coins/", views.trending_coins_proxy, name="trending-coins"),
    path("api/recently-listed/", views.recent_coins_proxy, name="recently-listed"),
    path("api/articles/", views.latest_insights, name="latest_insights"),
    path('api/futures-exchange-volumes/', views.fetch_futures_exchange_volumes, name='futures_exchange_volumes'),
    path('api/futures-open-interest/', views.fetch_futures_interest, name='futures_interest'),
    path('api/new-ath/', views.fetch_new_ath, name='new_ath'),






]
