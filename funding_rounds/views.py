from django.core.paginator import Paginator
from django.shortcuts import render
import pandas as pd

def funding_dashboard(request):
    try:
        overview = pd.read_csv("data/total_funding_overview.csv").to_dict(orient="records")[0]
    except Exception:
        overview = {}

    try:
        hot_rounds = pd.read_csv("data/hot_rounds.csv").to_dict(orient="records")
    except Exception:
        hot_rounds = []

    try:
        digest = pd.read_csv("data/fundraising_digest.csv").to_dict(orient="records")
    except Exception:
        digest = []

    try:
        # Load main funding data
        main_data = pd.read_csv("data/funding_main.csv").to_dict(orient="records")

        # Load funds
        df_funds = pd.read_csv("data/funding_funds.csv")
        funds_map = {}
        for _, row in df_funds.iterrows():
            funds_map.setdefault(row["coinKey"], []).append({
                "fund_name": row["fund_name"],
                "fund_image": row["fund_image"]
            })

        # Load followers
        df_followers = pd.read_csv("data/funding_followers.csv")
        followers_map = {}
        for _, row in df_followers.iterrows():
            followers_map.setdefault(row["coinKey"], []).append({
                "follower_name": row["follower_name"],
                "follower_image": row["follower_image"]
            })

        # Enrich records with related data
        for row in main_data:
            key = row.get("coinKey")
            row["funds"] = funds_map.get(key, [])
            row["followers"] = followers_map.get(key, [])

        paginator = Paginator(main_data, 20)
        page_number = request.GET.get("page")
        funding_main_page = paginator.get_page(page_number)

    except Exception:
        funding_main_page = []

    return render(request, "funding_rounds/funding_rounds.html", {
        "overview": overview,
        "hot_rounds": hot_rounds,
        "digest": digest,
        "funding_main_page": funding_main_page
    })
