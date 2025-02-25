import requests
import pandas as pd

def fetch_mobula_data():
    """Fetch cryptocurrency data from Mobula API with error handling."""
    url = "https://production-api.mobula.io/api/1/all"
    querystring = {
        "fields": (
            "logo,price,price_change_1h,price_change_24h,price_change_7d,"
            "price_change_1y,market_cap,liquidity,"
            "blockchains,chat,twitter,website"
        )
    }
    
    try:
        response = requests.get(url, params=querystring, timeout=10)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"API Request Failed: {e}")
        return None

def process_crypto_data(raw_data):
    """Process raw API response into structured DataFrame."""
    if not raw_data or 'data' not in raw_data:
        return pd.DataFrame()
    
    processed = []
    for asset in raw_data['data']:
        # 'contracts' is omitted in your code snippet, so we skip it here
        social = asset.get('chat', {})

        asset_data = {
            'id': asset.get('id'),
            'name': asset.get('name'),
            'symbol': asset.get('symbol'),
            'price': asset.get('price'),
            'market_cap': asset.get('market_cap'),
            'liquidity': asset.get('liquidity'),
            'blockchains': ', '.join(asset.get('blockchains', [])) or None,
            'price_change_1h': asset.get('price_change_1h'),
            'price_change_24h': asset.get('price_change_24h'),
            'price_change_7d': asset.get('price_change_7d'),
            'price_change_1y': asset.get('price_change_1y'),
            'twitter': asset.get('twitter'),
            'website': asset.get('website'),
            'logo': asset.get('logo'),
        }
        
        # Extract social links
        if isinstance(social, dict):
            for platform, link in social.items():
                asset_data[f'social_{platform.lower()}'] = link
        elif isinstance(social, list):
            asset_data['social'] = ', '.join(social)
        
        processed.append(asset_data)
    
    df = pd.DataFrame(processed)
    
    # Convert columns to numeric
    numeric_cols = [
        'price', 'market_cap', 'liquidity', 
        'price_change_1h', 'price_change_24h',
        'price_change_7d', 'price_change_1y'
    ]
    for col in numeric_cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce')

    # Drop rows with no price
    df = df.dropna(subset=['price'])

    # Fill missing text fields
    df['blockchains'].fillna('Unknown', inplace=True)
    df['twitter'].fillna('Unknown', inplace=True)
    df['website'].fillna('Unknown', inplace=True)

    # Fill missing logos with a default
    df['logo'].fillna('No Logo Available', inplace=True)

    return df

def run_pipeline_to_csv(csv_path='crypto_assets.csv'):
    """Convenience function that runs the entire pipeline and saves to CSV."""
    raw_data = fetch_mobula_data()
    if not raw_data:
        print("No data fetched.")
        return None
    
    df = process_crypto_data(raw_data)
    print(f"Found {len(df)} cryptocurrencies")
    df.to_csv(csv_path, index=False)
    return df
