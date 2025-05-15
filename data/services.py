import requests

def fetch_project_data(symbol):
    """
    Fetches project data for a given coin symbol.
    Replace the URL and parameters with those required by your API.
    """
    url = f"https://api.example.com/crypto/{symbol}"  # Update with the real API endpoint
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()
    return {"error": f"Failed to fetch data for {symbol}"}

# data/services/fund_cache.py
import requests

FUND_CACHE = {}

def load_fund_cache():
    global FUND_CACHE
    if not FUND_CACHE:
        all_funds = []
        for offset in range(0, 1000, 100):
            res = requests.get("https://api.cryptorank.io/v0/funds/table/", params={"limit": 100, "offset": offset})
            if res.status_code == 200:
                all_funds.extend(res.json().get("data", []))
        FUND_CACHE = {fund.get("slug"): fund for fund in all_funds}
    return FUND_CACHE
