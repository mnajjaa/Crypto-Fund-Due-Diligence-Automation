from django.shortcuts import render

# Create your views here.
from django.shortcuts import get_object_or_404, render
from django.http import JsonResponse
from .data_manager import load_watchlist, save_watchlist
from .services import fetch_project_data

def dashboard_view(request):
    """
    Render the dashboard page with the current watchlist.
    """
    watchlist = load_watchlist()
    return render(request, 'data/dashboard.html', {'watchlist': watchlist})

def project_data(request, symbol):
    """
    Fetch data for a given coin symbol via external API.
    """
    data = fetch_project_data(symbol)
    return JsonResponse(data)

def add_to_watchlist(request, symbol):
    """
    Add a coin symbol to the watchlist.
    """
    watchlist = load_watchlist()
    if symbol not in watchlist:
        watchlist.append(symbol)
        save_watchlist(watchlist)
    return JsonResponse({'status': 'added', 'symbol': symbol})






#####################################################
#Start dashFunds view
#####################################################

import requests
from django.shortcuts import render

from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.views.decorators.cache import cache_page

from data.services import load_fund_cache

@cache_page(60 * 5)
def dashFunds(request):
    watchlist = load_watchlist()

    # --- Fetch investors ---
    url_investors = "https://api.cryptorank.io/v0/funds/widgets/top-investors"
    response_investors = requests.get(url_investors)
    if response_investors.status_code == 200:
        investors_data = response_investors.json()
        investors = [{
            'name': i.get('name'),
            'logo': i.get('logo'),
            'count': i.get('count')
        } for i in investors_data]
        investor_names = [i['name'] for i in investors]
        investor_counts = [i['count'] for i in investors]
    else:
        investors, investor_names, investor_counts = [], [], []

    # --- Fetch investment focus ---
    url_focus = "https://api.cryptorank.io/v0/funds/widgets/investment-focus"
    r_focus = requests.get(url_focus)
    if r_focus.status_code == 200:
        focus_data = r_focus.json()
        investment_focus_names = [f['name'] for f in focus_data]
        investment_focus_percent = [f['percent'] for f in focus_data]
    else:
        investment_focus_names, investment_focus_percent = [], []

    # --- Get funds from shared cache ---
    fund_cache = load_fund_cache()
    funds = []
    for fund in fund_cache.values():
        retail_roi = fund.get("retailRoi")
        funds.append({
            "id": fund.get("id"),
            "slug": fund.get("slug"),
            "name": fund.get("name"),
            "logo": fund.get("logo"),
            "tier": fund.get("tier"),
            "type": fund.get("type"),
            "location": fund.get("location"),
            "latestDealName": fund.get("latestDeal", {}).get("name"),
            "latestDealDate": fund.get("latestDeal", {}).get("date"),
            "latestDealRaise": fund.get("latestDeal", {}).get("raise"),
            "portfolioCount": fund.get("portfolio"),
            "retailRoi": round(retail_roi, 2) if retail_roi is not None else "N/A",
            "focusArea": fund.get("focusArea"),
            "preferredStage": fund.get("preferredStage"),
            "fundingRounds": fund.get("fundingRounds"),
            "leadInvestments": fund.get("leadInvestments"),
            "mainFundingCountry": fund.get("mainFundingCountry"),
            "twitterUsername": (fund.get("twitterData") or {}).get("twitterUsername"),
            "followersCount": (fund.get("twitterData") or {}).get("followersCount"),
        })

    # --- Pagination ---
    paginator = Paginator(funds, 10)
    page = request.GET.get('page', 1)
    try:
        page_obj = paginator.page(page)
    except (PageNotAnInteger, EmptyPage):
        page_obj = paginator.page(1)

    return render(request, 'data/dashFunds.html', {
        'watchlist': watchlist,
        'investors': investors,
        'investor_names': investor_names,
        'investor_counts': investor_counts,
        'investment_focus_names': investment_focus_names,
        'investment_focus_percent': investment_focus_percent,
        'funds': page_obj.object_list,
        'page_obj': page_obj,
    })

#####################################################
#End dashFunds view
#####################################################

#####################################################
#Start Single Fund view
#####################################################
from django.shortcuts import render
from datetime import datetime, timedelta
from .services import FundAPITester  # Update path if needed

def single_fund_view(request, slug):
    tester = FundAPITester()

    # Get basic fund data (including id for other APIs)
    fund_data = tester.get_fund_data(slug)
    if not fund_data:
        return render(request, "404.html", {"message": f"Fund '{slug}' not found"}, status=404)

    fund_id = fund_data["basic"]["id"]
    today = datetime.today()
    one_year_ago = today - timedelta(days=365)
    start_date = one_year_ago.strftime("%Y-%m-%d")
    end_date = today.strftime("%Y-%m-%d")

    # Fetch additional data
    team = tester.get_team_data(slug)
    co_investors = tester.get_co_funds(fund_id)
    recent_fundings = tester.get_recent_funding(slug)
    countries = tester.get_funding_countries(slug)
    stages = tester.get_preferred_stages(slug)
    news = tester.get_news(slug)
    round_avg = tester.get_avg_round_raise(slug)
    country_activity = tester.get_investments_by_country(slug, start_date, end_date)
    monthly_investments = tester.get_investments_by_month(slug, start_date, end_date)
    social = tester.get_social_activity(fund_id)

    context = {
    "fund": fund_data,
    "team": team,
    "co_investors": co_investors,
    "recent_fundings": recent_fundings,
    "countries": countries,
    "stages": stages,
    "news": news,
    "round_avg": round_avg,
    "round_avg_labels": [r["range"] for r in round_avg],
    "round_avg_values": [r["percentage"] for r in round_avg],
    "country_activity": country_activity,
    "monthly_investments": monthly_investments,
    "social": social,
}


    return render(request, "singleFund.html", context)



#####################################################
def single_fund_view_2(request, slug):
    fund = load_fund_cache().get(slug)
    if not fund:
        return render(request, "404.html", {"message": "Fund not found"}, status=404)

    return render(request, 'data/singleFund.html', {
        'fund': fund,
        'id': fund.get('id'),
        'name': fund.get('name'),
        'slug': fund.get('slug'),
    })

from django.http import JsonResponse
from data.utils import fetch_focus_area_data, load_focus_area_from_csv

def focus_area_view(request, slug):
    data = fetch_focus_area_data(slug)
    if not data:
        data = load_focus_area_from_csv(slug)
    return JsonResponse({"slug": slug, "data": data})


# views.py
import requests
from django.shortcuts import render
from concurrent.futures import ThreadPoolExecutor

def get_fund_data(request):
    # Base configuration
    fund_slug = "coinbase-ventures"
    fund_id = 5  # Example fund ID
    api_base = "https://api.cryptorank.io/v0"
    
    # API endpoints dictionary
    endpoints = {
        'fund_details': f"{api_base}/coin-funds/by-slug/{fund_slug}/?locale=en",
        'focus_area': f"{api_base}/coin-funds/focus-area/{fund_slug}",
        'social_activity': f"{api_base}/coin-funds/{fund_id}/social-activity",
        'funding_countries': f"{api_base}/coin-funds/main-funding-countries/{fund_slug}",
        'avg_round': f"{api_base}/coin-funds/avg-round-raise/{fund_slug}",
        'team': f"{api_base}/team/by-fund-key/{fund_slug}",
        'preferred_stage': f"{api_base}/coin-funds/preferred-stage/{fund_slug}",
        'recent_rounds': f"{api_base}/coin-funds/recent-funding-rounds/{fund_slug}",
        'co_funds': f"{api_base}/coin-funds/{fund_id}/co-funds",
        'investments_by_month': f"{api_base}/fund-chart/{fund_slug}/investments-count-by-month",
        'investments_by_country': f"{api_base}/fund-chart/{fund_slug}/investments-count-by-country",
        'news': f"{api_base}/news?lang=en&limit=4&fundsSlugs={fund_slug}",
    }

    context = {}
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/132.0.0.0 Safari/537.36 OPR/117.0.0.0'}

    def fetch_data(url_key):
        try:
            response = requests.get(endpoints[url_key], headers=headers)
            response.raise_for_status()
            return {url_key: response.json()}
        except Exception as e:
            print(f"Error fetching {url_key}: {str(e)}")
            return {url_key: None}

    # Fetch data in parallel
    with ThreadPoolExecutor(max_workers=5) as executor:
        results = executor.map(fetch_data, endpoints.keys())
        for result in results:
            context.update(result)

    # Process data for template
    processed_data = {
        'fund': context.get('fund_details', {}).get('data', {}),
        'focus_areas': context.get('focus_area', {}).get('data', []),
        'social': context.get('social_activity', {}).get('data', {}),
        'countries': context.get('funding_countries', {}).get('data', []),
        'avg_round': context.get('avg_round', {}).get('data', {}),
        'team': context.get('team', {}).get('data', []),
        'stages': context.get('preferred_stage', {}).get('data', []),
        'recent_rounds': context.get('recent_rounds', {}).get('data', []),
        'co_funds': context.get('co_funds', {}).get('data', []),
        'investments_chart': context.get('investments_by_month', {}).get('data', {}),
        'country_data': context.get('investments_by_country', {}).get('data', []),
        'news': context.get('news', {}).get('data', []),
    }

    return render(request, 'fund_dashboard.html', {'data': processed_data})

#####################################################
#End Single Fund view
#####################################################