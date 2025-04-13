import requests
from datetime import datetime, timedelta
from django.shortcuts import render
import logging

# Set up logging
logger = logging.getLogger(__name__)

def fundraising_chart(request):
    """
    Render the fundraising chart page with data from the API.
    """
    # === Fetch Fundraising Data ===
    url_fundraising = "https://api.cryptorank.io/v0/fund-chart/crypto-fundraising-activity?groupBy=month&startDate=2022-04-01&endDate=2025-04-08"
    response_fundraising = requests.get(url_fundraising)

    if response_fundraising.status_code == 200:
        try:
            fundraising_data = response_fundraising.json()
            chart_data = []
            for item in fundraising_data:
                date = datetime.strptime(item['date'], "%Y-%m-%dT%H:%M:%S.%fZ")
                formatted_date = date.strftime("%b, %y")
                chart_data.append({
                    'month': formatted_date,
                    'raise': item['raise'],
                    'count': item['count']
                })
        except (ValueError, KeyError) as e:
            logger.error(f"Error processing fundraising data: {e}")
            chart_data = []
    else:
        logger.error(f"Failed to fetch fundraising data: {response_fundraising.status_code}")
        chart_data = []

    # === Fetch Most Active Angels Data ===
    url_angels = "https://api.cryptorank.io/v0/fund-chart/most-active-angels?startDate=2024-04-01&endDate=2025-04-08"
    response_angels = requests.get(url_angels)

    if response_angels.status_code == 200:
        try:
            angels_data = response_angels.json()
            angels_data_formatted = [
                {
                    'slug': item['slug'],
                    'name': item['name'],
                    'logo': item['logo'],
                    'lead': item['lead'],
                    'normal': item['normal'],
                    'total': item['total']
                }
                for item in angels_data
            ]
        except (ValueError, KeyError) as e:
            logger.error(f"Error processing angels data: {e}")
            angels_data_formatted = []
    else:
        logger.error(f"Failed to fetch angels data: {response_angels.status_code}")
        angels_data_formatted = []

    # === Fetch Most Active Funds Data ===
    url_funds = "https://api.cryptorank.io/v0/fund-chart/most-active-funds?startDate=2024-04-01&endDate=2025-04-08"
    response_funds = requests.get(url_funds)

    if response_funds.status_code == 200:
        try:
            funds_data = response_funds.json()
            funds_data_formatted = [
                {
                    'slug': item['slug'],
                    'name': item['name'],
                    'logo': item['logo'],
                    'lead': item['lead'],
                    'normal': item['normal'],
                    'total': item['total']
                }
                for item in funds_data
            ]
        except (ValueError, KeyError) as e:
            logger.error(f"Error processing funds data: {e}")
            funds_data_formatted = []
    else:
        logger.error(f"Failed to fetch funds data: {response_funds.status_code}")
        funds_data_formatted = []

    # === Fetch Number of Funding Rounds by Investor and Category ===
    url_categories = "https://api.cryptorank.io/v0/fund-chart/number-of-funding-rounds-by-investor-and-category?startDate=2024-10-01&endDate=2025-04-10"
    response_categories = requests.get(url_categories)

    if response_categories.status_code == 200:
        try:
            categories_data = response_categories.json().get('data', [])
            categories_data_formatted = [
                {
                    'name': item['name'],
                    'slug': item['slug'],
                    'categories': item['categories']
                }
                for item in categories_data
            ]
        except (ValueError, KeyError) as e:
            logger.error(f"Error processing categories data: {e}")
            categories_data_formatted = []
    else:
        logger.error(f"Failed to fetch categories data: {response_categories.status_code}")
        categories_data_formatted = []

    # === Fetch Fundraising Rounds by Size ===
    url_rounds_by_size = "https://api.cryptorank.io/v0/fund-chart/fundraising-rounds-by-size?startDate=2022-04-01&endDate=2025-04-10"
    response_rounds_by_size = requests.get(url_rounds_by_size)

    if response_rounds_by_size.status_code == 200:
        try:
            rounds_by_size_data = response_rounds_by_size.json()
            rounds_by_size_formatted = [
                {
                    'name': f"{item['raiseFrom'] / 1000000:.0f} - {item['raiseTo'] / 1000000 if item['raiseTo'] else '+'}M",
                    'count': item['count'],
                    'countPercent': item['countPercent']
                }
                for item in rounds_by_size_data['raiseGroups']
            ]
            total_rounds = sum(item['count'] for item in rounds_by_size_data['raiseGroups'])
        except (ValueError, KeyError) as e:
            logger.error(f"Error processing rounds by size data: {e}")
            rounds_by_size_formatted = []
            total_rounds = 0
    else:
        logger.error(f"Failed to fetch rounds by size data: {response_rounds_by_size.status_code}")
        rounds_by_size_formatted = []
        total_rounds = 0

    # === Fetch Monthly Fundraising by Category ===
    url_monthly_funding = "https://api.cryptorank.io/v0/fund-chart/monthly-funding-investment-by-category?groupBy=month&startDate=2020-04-06&endDate=2025-04-10"
    response_monthly_funding = requests.get(url_monthly_funding)

    if response_monthly_funding.status_code == 200:
        try:
            monthly_funding_data = response_monthly_funding.json()
            monthly_funding_formatted = []
            for item in monthly_funding_data:
                date = datetime.strptime(item['date'], "%Y-%m-%dT%H:%M:%S.%fZ")
                formatted_date = date.strftime("%b, %y")
                monthly_funding_formatted.append({
                    'date': formatted_date,
                    'categories': item['categories']
                })
        except (ValueError, KeyError) as e:
            logger.error(f"Error processing monthly funding data: {e}")
            monthly_funding_formatted = []
    else:
        logger.error(f"Failed to fetch monthly funding data: {response_monthly_funding.status_code}")
        monthly_funding_formatted = []

    # === Fetch Heatmap of Investment Locations Data ===
    url_heatmap = "https://api.cryptorank.io/v0/fund-chart/country-heatmap?startDate=2022-04-10&endDate=2025-04-10"
    response_heatmap = requests.get(url_heatmap)

    if response_heatmap.status_code == 200:
        try:
            heatmap_data = response_heatmap.json()
            heatmap_data_formatted = [
                {
                    'country': item['country'],
                    'raise': item['raise'],
                    'rounds': item['rounds']
                }
                for item in heatmap_data
            ]
        except (ValueError, KeyError) as e:
            logger.error(f"Error processing heatmap data: {e}")
            heatmap_data_formatted = []
    else:
        logger.error(f"Failed to fetch heatmap data: {response_heatmap.status_code}")
        heatmap_data_formatted = []
    # === Fetch Most Active Crypto VC Jurisdictions Data ===
    url_vc_jurisdictions = "https://api.cryptorank.io/v0/fund-chart/most-active-crypto-vc-jurisdictions?startDate=2024-10-12&endDate=2025-04-12"
    response_vc_jurisdictions = requests.get(url_vc_jurisdictions)
    
    if response_vc_jurisdictions.status_code == 200:
        try:
            vc_jurisdictions_data = response_vc_jurisdictions.json().get('data', [])
            vc_jurisdictions_formatted = [
                {
                    'countryCode': item['country']['code'].lower(),  # Highcharts Maps expects lowercase country codes (e.g., 'us')
                    'countryName': item['country']['name'],
                    'count': item['count'],
                    'percentChange': item['percentChange'],
                    'categories': [
                        {
                            'name': cat['name'],
                            'count': cat['count'],
                            'percent': cat['percent']
                        }
                        for cat in item['categories']
                    ]
                }
                for item in vc_jurisdictions_data
            ]
        except (ValueError, KeyError) as e:
            logger.error(f"Error processing VC jurisdictions data: {e}")
            vc_jurisdictions_formatted = []
    else:
        logger.error(f"Failed to fetch VC jurisdictions data: {response_vc_jurisdictions.status_code}")
        vc_jurisdictions_formatted = []
    
    # Render the template with all data
    return render(request, 'fundraising_chart.html', {
        'chart_data': chart_data,
        'angels_data': angels_data_formatted,
        'funds_data': funds_data_formatted,
        'categories_data': categories_data_formatted,
        'rounds_by_size_data': rounds_by_size_formatted,
        'total_rounds': total_rounds,
        'monthly_funding_data': monthly_funding_formatted,
        'heatmap_data': heatmap_data_formatted,
        'vc_jurisdictions_data': vc_jurisdictions_formatted  # Add new data to context
    })
