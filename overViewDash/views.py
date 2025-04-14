from django.shortcuts import render

# Create your views here.
def overview_dashboard(request):
    return render(request, "overViewDash/overViewDash.html")

def firstPageCards(request):
    return render(request, 'componentFirstPage/upcard.html')
import requests
from django.http import JsonResponse

def coin_list_proxy(request):
    url = "https://cryptorank.io/all-coins-list"
    response = requests.get(url)
    return JsonResponse(response.json(), safe=False)

def btc_dominance_proxy(request):
    period = request.GET.get('period', '7D')
    url = f"https://api.cryptorank.io/v0/widgets/btc-dominance-chart?period={period}"
    
    try:
        response = requests.get(url)
        response.raise_for_status()
        return JsonResponse(response.json(), safe=False)
    except requests.RequestException as e:
        return JsonResponse({'error': 'Failed to fetch data'}, status=500)
    


def hotEvents_proxy(request):
    url = "https://api.cryptorank.io/v0/widgets/hot-events"
    response = requests.get(url)
    return JsonResponse(response.json(), safe=False)
from django.http import JsonResponse
import requests
from datetime import datetime
from datetime import timedelta

def topgainer_proxy(request):
    url = "https://api.cryptorank.io/v0/coins/v2?specialFilter=topGainersFor24h&limit=150&locale=en"  # the actual top gainers URL

    try:
        response = requests.get(url, timeout=10)
        if response.status_code == 200 and response.text.strip():
            return JsonResponse(response.json(), safe=False)
        else:
            return JsonResponse({'error': 'Invalid or empty response from upstream API'}, status=502)
    except requests.exceptions.RequestException as e:
        return JsonResponse({'error': str(e)}, status=500)

def toplosers_proxy(request):
    url = "https://cryptorank.io/_next/data/1744212217147/en/losers.json"  # the actual top gainers URL

    try:
        response = requests.get(url, timeout=10)
        if response.status_code == 200 and response.text.strip():
            return JsonResponse(response.json(), safe=False)
        else:
            return JsonResponse({'error': 'Invalid or empty response from upstream API'}, status=502)
    except requests.exceptions.RequestException as e:
        return JsonResponse({'error': str(e)}, status=500)
def gainers_loser_24h(request):
    name = request.GET.get('name', '')
    url = f"https://api.cryptorank.io/v0/coins/historical-prices?keys={name}"
    try:
        response = requests.get(url)
        response.raise_for_status()
        return JsonResponse(response.json(), safe=False)
    except requests.RequestException:
        return JsonResponse({'error': 'Failed to fetch data'}, status=500)
    
from django.http import JsonResponse
from datetime import datetime, timedelta
import requests

def fundraising_chart_proxy(request):
    end_date = datetime.today().strftime('%Y-%m-%d')
    start_date = (datetime.today() - timedelta(days=365)).strftime('%Y-%m-%d')

    group_by = request.GET.get('groupBy', 'month')  # optional frontend control

    url = f"https://api.cryptorank.io/v0/fund-chart/crypto-fundraising-activity?groupBy={group_by}&startDate={start_date}&endDate={end_date}"
    response = requests.get(url)
    return JsonResponse(response.json(), safe=False)

def ido_chart_proxy(request):
    end_date = datetime.today().strftime('%Y-%m-%d')
    start_date = (datetime.today() - timedelta(days=365)).strftime('%Y-%m-%d')

    group_by = request.GET.get('groupBy', 'month')  # optional frontend control

    url = f"https://api.cryptorank.io/v0/public-raise-dashboard/raise?groupBy={group_by}&startDate={start_date}&endDate={end_date}"
    response = requests.get(url)
    return JsonResponse(response.json(), safe=False)
import pandas as pd
import os
from django.conf import settings
def overviewido_dashboard(request):
 try:
        csv_path = os.path.join(settings.BASE_DIR, "data", "upcoming_rounds.csv")
        df = pd.read_csv(csv_path)
        upcoming_rounds = df.to_dict(orient="records")
        print("✅ Loaded:", len(upcoming_rounds))
 except Exception as e:
        print(f"❌ Error loading CSV: {e}")
        upcoming_rounds = []

 return render(request, "overViewDash/overViewDash.html", {
        "upcoming_rounds": upcoming_rounds,
    })
def fear_greed(request):
    url = f"https://api.cryptorank.io/v0/widgets/fear-and-greed-index"
    response = requests.get(url)
    return JsonResponse(response.json(), safe=False)

def launchpads_roi_proxy(request):
    url = "https://api.cryptorank.io/v0/public-raise-dashboard/top-launchpad-platforms"
    params = {
        "startDate": "2024-04-06T12:31:03.416Z",
        "endDate": "2025-04-06T12:31:03.416Z"
    }
    try:
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        return JsonResponse(response.json(), safe=False)
    except requests.RequestException as e:
        return JsonResponse({"error": "Failed to fetch launchpads ROI data"}, status=500)



def market_state_proxy(request):
    url = "https://api.cryptorank.io/v0/coins/heatmap-by-market-cap?limit=50&locale=en"
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        return JsonResponse(response.json(), safe=False)
    except requests.RequestException as e:
        return JsonResponse({"error": "Failed to fetch market state data"}, status=500)



def trending_coins_proxy(request):
    url = "https://api.cryptorank.io/v0/coins/trending-coins?limit=10"
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        return JsonResponse(response.json(), safe=False)
    except requests.RequestException:
        return JsonResponse({'error': 'Error loading trending coins.'}, status=500)


def recent_coins_proxy(request):
    url = "https://api.cryptorank.io/v0/coins/recently-added?limit=10"
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        return JsonResponse(response.json(), safe=False)
    except requests.RequestException:
        return JsonResponse({'error': 'Error loading trending coins.'}, status=500)



def latest_insights(request):
    url = "https://api.cryptorank.io/v0/articles?category=insights&locale=en"
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        return JsonResponse(response.json(), safe=False)
    except requests.RequestException:
        return JsonResponse({'error': 'Error loading articles.'}, status=500)





def fetch_futures_exchange_volumes(request):
    url = "https://api.cryptorank.io/v0/analytics/futures/exchange-volumes?key=bitcoin&limit=10"
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        return JsonResponse(response.json(), safe=False)
    except requests.RequestException:
        return JsonResponse({'error': 'Error loading data.'}, status=500)


def fetch_futures_interest(request):
    url = "https://api.cryptorank.io/v0/analytics/futures/exchange-interest?key=bitcoin&limit=8"
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        return JsonResponse(response.json(), safe=False)
    except requests.RequestException:
        return JsonResponse({'error': 'Error loading data.'}, status=500)





def fetch_new_ath(request):
    # Define the API endpoint
    url = "https://cryptorank.io/_next/data/1744640559751/en/ath.json"
    
    try:
        # Send a GET request to the API
        response = requests.get(url, timeout=10)
        response.raise_for_status()  # Raise an exception for HTTP errors
        
        # If the response is successful, parse the JSON and return it
        data = response.json()
        ath_data = data.get('pageProps', {}).get('fallbackData', [])[:6]  # Get the top 6 items
        
        return JsonResponse(ath_data, safe=False)  # Return the data as JSON
        
    except requests.RequestException:
        # If there is any error, return a message with an error status
        return JsonResponse({'error': 'Error loading data.'}, status=500)




import pandas as pd
import os
from django.conf import settings
from django.shortcuts import render

import os
import pandas as pd
from django.shortcuts import render
import json
def overview_page(request):
    selected_period = request.GET.get("period", "7D")
    periods = ["24H", "7D", "1M", "1Y"]
    if selected_period not in periods:
        selected_period = "7D"

    try:
        hot_events = pd.read_csv("data/hot_events.csv").to_dict(orient="records")
    except:
        hot_events = []

    try:
        fear_greed = pd.read_csv("data/data_fear_greed.csv").to_dict(orient="records")
    except:
        fear_greed = []

    btc_data = {}
    for period in periods:
        try:
            path = f"data/btc_dominance/btc_dominance_{period}.csv"
            btc_data[period] = pd.read_csv(path).to_dict(orient="records")
        except:
            btc_data[period] = []
        try:
           funding_trend = pd.read_csv("data/fundraising_trend.csv").to_dict(orient="records")
        except:
           funding_trend = []
        try:
           funding_ido = pd.read_csv("data/fundraising_ido.csv").to_dict(orient="records")
        except:
           funding_ido = []
        try:
           gainers = pd.read_csv("data/top_gainers.csv").to_dict(orient="records")
        except:
           gainers = []
        try:
         upcoming_ido = pd.read_csv("data/upcoming_ido.csv").fillna("").to_dict(orient="records")
        # Replace NaN values with None to make it JSON serializable
        except Exception:
         upcoming_ido = []
        try:
         upcoming_funds= pd.read_csv("data/upcoming_funds.csv").fillna("").to_dict(orient="records")
        # Replace NaN values with None to make it JSON serializable
        except Exception:
         upcoming_funds = []
    try:
     coins_list = pd.read_csv("data/coins_list_clean_ready.csv").fillna("").to_dict(orient="records")
        # Replace NaN values with None to make it JSON serializable
    except Exception:
        coins_list = []

    return render(request, "index.html", {
        "btc_data": json.dumps(btc_data),  # ✅ add json.dumps here!
        "selected_period": selected_period,
        'fear_greed': json.dumps(fear_greed),  # serialize here
        "hot_events": json.dumps(hot_events),  # ✅ must be json.dumps!
        "funding_trend": json.dumps(funding_trend), 
        "funding_ido": json.dumps(funding_ido),
        "gainers": json.dumps(gainers), 
        "upcoming_ido": json.dumps(upcoming_ido),
        "coins_list": json.dumps(coins_list),
        "upcoming_funds": json.dumps(upcoming_funds),
 # serialize here
          # serialize here
    })


