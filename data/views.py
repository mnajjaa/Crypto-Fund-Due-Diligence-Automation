from django.shortcuts import render
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

import requests
from django.shortcuts import render

import requests
from django.shortcuts import render

import requests
from django.shortcuts import render

import requests
from django.shortcuts import render

def dashFunds(request):
    """
    Render the dashboard page with the current watchlist, top investors, and crypto funds.
    """
    # Fetch the watchlist
    watchlist = load_watchlist()

    # === Fetch Top Investors ===
    url_investors = "https://api.cryptorank.io/v0/funds/widgets/top-investors"
    response_investors = requests.get(url_investors)

    if response_investors.status_code == 200:
        investors_data = response_investors.json()
        investors = []
        investor_names = []
        investor_counts = []
        for investor in investors_data:
            investors.append({
                'name': investor.get('name'),
                'logo': investor.get('logo'),
                'count': investor.get('count')
            })
            investor_names.append(investor.get('name'))
            investor_counts.append(investor.get('count'))
    else:
        investors, investor_names, investor_counts = [], [], []

    # === Fetch Investment Focus ===
    url_investment_focus = "https://api.cryptorank.io/v0/funds/widgets/investment-focus"
    response_investment_focus = requests.get(url_investment_focus)

    if response_investment_focus.status_code == 200:
        investment_focus_data = response_investment_focus.json()
        investment_focus_names = [focus['name'] for focus in investment_focus_data]
        investment_focus_percent = [focus['percent'] for focus in investment_focus_data]
    else:
        investment_focus_names, investment_focus_percent = [], []

    # === Fetch the Top 1000 Funds ===
    base_url = "https://api.cryptorank.io/v0/funds/table/"
    all_funds = []

    for offset in range(0, 1000, 100):
        params = {"limit": 100, "offset": offset}
        res = requests.get(base_url, params=params)
        if res.status_code == 200:
            data = res.json()
            all_funds.extend(data.get("data", []))

        else:
            print(f"Failed to fetch data at offset {offset}")

    # === Clean and Structure the Funds Data ===
    funds = []
    for fund in all_funds:
        retail_roi = fund.get("retailRoi")
    
        funds.append({
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

    return render(request, 'data/dashFunds.html', {
        'watchlist': watchlist,
        'investors': investors,
        'investor_names': investor_names,
        'investor_counts': investor_counts,
        'investment_focus_names': investment_focus_names,
        'investment_focus_percent': investment_focus_percent,
        'funds': funds  
    })


















#####################################################
#End dashFunds view
#####################################################