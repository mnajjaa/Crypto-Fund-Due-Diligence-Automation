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
