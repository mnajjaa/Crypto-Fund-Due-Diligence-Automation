from django.shortcuts import render
import requests
from django.http import JsonResponse
        
def firstPage(request):
    return render(request, 'firstPage.html')
def firstPageCards(request):
    return render(request, 'componentFirstPage/upcard.html')


def coin_list_proxy(request):
    url = "https://cryptorank.io/_next/data/1744212217147/en/all-coins-list.json"
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



