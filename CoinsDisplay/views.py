from django.conf import settings
import requests
from django.http import JsonResponse
from django.shortcuts import render
from urllib.parse import urlparse, parse_qs, urlencode, urlunparse
import time
from django.views.decorators.csrf import csrf_exempt

def fetch_crypto_data():
    # List of cryptocurrencies to fetch with their symbols
    target_coins = {
        'BTC': 'Bitcoin',
        'ETH': 'Ethereum',
        'XRP': 'XRP',
        'BNB': 'BNB',
        'SOL': 'Solana',
        'USDC': 'USD Coin',
        'DOGE': 'Dogecoin',
        'TRX': 'TRON',
        'ADA': 'Cardano',
        'LINK': 'Chainlink',
        'AVAX': 'Avalanche',
        'TON': 'Toncoin',
        'XLM': 'Stellar',
        'SUI': 'Sui',
        'BCH': 'Bitcoin Cash',
        'LTC': 'Litecoin',
        'DOT': 'Polkadot',
        'XMR': 'Monero',
        'ONDO': 'Ondo',
        'NEAR': 'NEAR Protocol',
        'ETC': 'Ethereum Classic',
        'ICP': 'Internet Computer',
        'TAO': 'Bittensor',
        'CRO': 'Cronos',
        'MNT': 'Mantle',
        'AAEV': 'Aaev',
        'VET': 'VeChain',
        'KAS': 'Kaspa',
        'POL': 'Polygon',
        'ATOM': 'Cosmos',
        'ALGO': 'Algorand',
        'FIL': 'Filecoin',
        'ENA': 'Ethena',
        'TIA': 'Celestia',
        'FET': 'Fetch.ai',
        'DEXE': 'Dexe',
        'MKR': 'Maker',
        'XDC': 'XDC Network',
        'OP': 'Optimism',
        'JUP': 'Jupiter',
        'IP': 'Story',
        'FLR': 'Flare',
        'EOS': 'EOS',
        'BONK': 'Bonk',
        'STX': 'Stacks',
        'WLD': 'Worldcoin',
        'SEI': 'Sei',
        'INJ': 'Injective',
        'CRV': 'Curve DAO Token',
        'QNT': 'Quant',
        'PAXG': 'PAX Gold',
        'GRT': 'The Graph',
        'THETA': 'Theta Network',
        'LDO': 'Lido DAO',
        'HNT': 'Helium'
    }

    url = 'https://pro-api.coinmarketcap.com/v1/cryptocurrency/listings/latest'
    headers = {
        'Accepts': 'application/json',
        'X-CMC_PRO_API_KEY': settings.COINMARKETCAP_API_KEY,
    }
    params = {
        'start': '1',
        'limit': '100',  # May need to adjust if you have more than 100 coins
        'convert': 'USD'
    }

    response = requests.get(url, headers=headers, params=params)
    data = response.json().get('data', [])

    coins = []
    for coin in data:
        symbol = coin['symbol']
        if symbol in target_coins:
            coins.append({
                'id': coin['id'],
                'name': coin['name'],
                'symbol': symbol,
                'price': coin['quote']['USD']['price'],
                'change24h': coin['quote']['USD']['percent_change_24h'],
                'marketCap': coin['quote']['USD']['market_cap'],
                'logo': f"https://s2.coinmarketcap.com/static/img/coins/64x64/{coin['id']}.png",
            })

            # Remove found coin from target list
            target_coins.pop(symbol, None)

            # Early exit if we've found all coins
            if not target_coins:
                break

    return coins
def coins_view(request):
    try:
        coins = fetch_crypto_data()
        return render(request, 'coins_view.html', {'coins': coins})
    except Exception as e:
        return render(request, 'coins_view.html', {'coins': [], 'error': str(e)})
    
def get_candles(request, symbol):
    try:
        url = f'https://api.kucoin.com/api/v1/market/candles?type=1hour&symbol={symbol}-USDT'
        res = requests.get(url)
        candles = res.json().get('data', [])

        data = [
            {
                'time': int(c[0]),
                'open': float(c[1]),
                'high': float(c[2]),
                'low': float(c[3]),
                'close': float(c[4]),
            }
            for c in candles
        ]

        return JsonResponse(data, safe=False)

    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


def get_coin_info(request, coin_id):
    try:
        url = 'https://pro-api.coinmarketcap.com/v2/cryptocurrency/info'
        headers = {
            'Accepts': 'application/json',
            'X-CMC_PRO_API_KEY': settings.COINMARKETCAP_API_KEY,
        }
        params = {'id': str(coin_id)}  # Critical: CoinMarketCap expects string IDs

        response = requests.get(url, headers=headers, params=params)

        if response.status_code != 200:
            return JsonResponse({
                'error': f"CoinMarketCap API Error: {response.status_code}",
                'details': response.text
            }, status=500)

        data = response.json().get('data', {})
        coin_data = data.get(str(coin_id))  # Key must match the string ID

        if not coin_data:
            return JsonResponse({
                'error': 'Coin data not found',
                'received_data': data
            }, status=404)

        return JsonResponse({
            'website': coin_data.get('urls', {}).get('website', [None])[0],
            'whitepaper': coin_data.get('urls', {}).get('whitepaper', [None])[0],
            'source_code': coin_data.get('urls', {}).get('source_code', [None])[0],
            'explorers': coin_data.get('urls', {}).get('explorer', [])[:3],
            'categories': coin_data.get('category', 'N/A'),
            'wallets': coin_data.get('urls', {}).get('wallet', [])[:3],
        })

    except Exception as e:
        return JsonResponse({
            'error': str(e),
            'traceback': traceback.format_exc()
        }, status=500)

#Whale alerts
def time_ago(timestamp):
    now = int(time.time())
    diff = now - timestamp
    if diff < 60:
        return f"{diff} secs"
    elif diff < 3600:
        return f"{diff // 60} mins"
    elif diff < 86400:
        return f"{diff // 3600} hours"
    else:
        return f"{diff // 86400} days"

def fetch_whale_alerts(request):  # <-- now accepts `request`
    base_url = "https://whale-alert.io/alerts.json?start=1741993200&end=1744585199"
    end_timestamp = int(time.time())
    start_timestamp = end_timestamp - 86400  # 24h ago

    parsed = urlparse(base_url)
    query = parse_qs(parsed.query)
    query['start'] = [str(start_timestamp)]
    query['end'] = [str(end_timestamp)]
    final_url = urlunparse(parsed._replace(query=urlencode(query, doseq=True)))

    response = requests.get(final_url)
    alerts_data = []

    if response.status_code == 200:
        alerts = response.json()
        if isinstance(alerts, list):
            for tx in alerts:
                timestamp = tx.get('timestamp', 0)
                ago = time_ago(timestamp)
                text = tx.get('text', '')
                emoticons = tx.get('emoticons', '🐋')
                amounts = tx.get('amounts', [])

                for amt in amounts:
                    alerts_data.append({
                        'symbol': amt.get('symbol', '???').upper(),
                        'amount': amt.get('amount', 0),
                        'value_usd': amt.get('value_usd', 0),
                        'ago': ago,
                        'text': text,
                        'emoticons': emoticons
                    })

    return JsonResponse({'alerts': alerts_data})

#fund investments
@csrf_exempt
def fetch_investment_data(request):
    group_by = request.GET.get('groupBy', 'month')
    start_date = request.GET.get('startDate', '2023-04-01')
    end_date = request.GET.get('endDate')

    url = f"https://api.cryptorank.io/v0/public-raise-dashboard/investment-trend?groupBy={group_by}&startDate={start_date}&endDate={end_date}"

    try:
        response = requests.get(url)
        return JsonResponse(response.json(), safe=False)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@csrf_exempt
def fetch_raise_data(request):
    group_by = request.GET.get('groupBy', 'month')
    start_date = request.GET.get('startDate', '2023-04-01')
    end_date = request.GET.get('endDate')

    url = f"https://api.cryptorank.io/v0/public-raise-dashboard/raise?groupBy={group_by}&startDate={start_date}&endDate={end_date}"

    print("Fetching URL:", url)
    try:
        response = requests.get(url)
        return JsonResponse(response.json(), safe=False)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@csrf_exempt
def fetch_raise_and_projects_on_blockchains(request):
    start_date = request.GET.get('startDate', '2023-04-01')
    end_date = request.GET.get('endDate')

    url = f"https://api.cryptorank.io/v0/public-raise-dashboard/raise-and-projects-on-blockchains?startDate={start_date}&endDate={end_date}"

    print("Fetching URL:", url)

    try:
        response = requests.get(url)
        response.raise_for_status()
        raw_data = response.json()

        # Optional: filter out only useful fields
        simplified_data = [
            {
                "name": item.get("name"),
                "key": item.get("key"),
                "projects":item.get("projects"),
                "sum": item.get("sum")
            }
            for item in raw_data.get("data", [])
        ]

        return JsonResponse({"data": simplified_data}, safe=False)

    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@csrf_exempt
def fetch_token_sales_by_type(request):

    start_date = request.GET.get('startDate', '2023-04-01')
    end_date = request.GET.get('endDate')

    url = f"https://api.cryptorank.io/v0/public-raise-dashboard/public-rounds-by-type?startDate={start_date}&endDate={end_date}"

    print("Fetching URL:", url)
    try:
        response = requests.get(url)
        return JsonResponse(response.json(), safe=False)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)
    
def fund_investments(request):
    return render(request, 'fund_investments.html')