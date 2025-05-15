from django.core.paginator import Paginator
from django.shortcuts import render
import pandas as pd
from collections import defaultdict
import ast
from django.utils.safestring import mark_safe
import ast
from datetime import datetime

import json


def funding_dashboard(request):
    try:
# Read and process overview data
        overview = pd.read_csv("data/total_funding_overview.csv").to_dict(orient="records")[0]
        
        # Process averageRoundSize
        if 'averageRoundSize' in overview:
            try:
                # Clean and convert format
                clean_str = overview['averageRoundSize'].replace('$', '').replace(',', '').replace(' ', '')
                min_val, max_val = clean_str.split('-')
                overview['averageRoundSize'] = f"{int(int(min_val)/1_000_000)}-{int(int(max_val)/1_000_000)}"
            except Exception as e:
                print(f"Error processing averageRoundSize: {e}")
                overview['averageRoundSize'] = "N/A"
    except Exception as e:
        print(f"Error loading overview data: {e}")
        overview = {}

    try:
        df = pd.read_csv("data/hot_rounds.csv")
        df["funds"] = df["funds"].apply(ast.literal_eval)
        hot_rounds = df.to_dict(orient="records")
    except Exception:
        hot_rounds = []

    try:
        df = pd.read_csv("data/fundraising_digest.csv")
        print("CSV loaded rows:", len(df))

        print("First row before parsing:", df.iloc[0].to_dict())

        df["tags"] = df["tags"].apply(ast.literal_eval)
        
        # Add this line to clean NaN values
        df = df.where(pd.notnull(df), None)  # 🆕 THIS IS THE FIX
        
        print("First row after parsing tags:", df.iloc[0].to_dict())

        digest = json.loads(df.to_json(orient="records", date_format="iso"))
        print("Sample digest entry:", digest[0] if digest else "EMPTY")

    except Exception as e:
        print("Digest CSV Load Error:", e)
        digest = []

    # ✅ Add this right here:
    for item in digest:
        try:
            item["publishDate"] = datetime.strptime(item["publishDate"], "%Y-%m-%dT%H:%M:%S.%fZ")
        except Exception as e:
            print("Invalid date format:", item.get("publishDate"), e)
            item["publishDate"] = None

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

                try:
                    if row.get("date"):
                        row["date"] = datetime.strptime(row["date"], "%Y-%m-%dT%H:%M:%S.%fZ")
                except Exception as e:
                    print("Invalid date in funding row:", row.get("date"), e)
                    row["date"] = None

                raw_raise = row.get("raise")
                try:
                    val = float(raw_raise)
                    if val >= 1_000_000:
                        row["formatted_raise"] = f"${val / 1_000_000:.2f}M"
                    elif val >= 1_000:
                        row["formatted_raise"] = f"${val / 1_000:.2f}K"
                    elif val > 0:
                        row["formatted_raise"] = f"${val:.0f}"
                    else:
                        row["formatted_raise"] = "N/A"
                except Exception:
                    row["formatted_raise"] = "N/A"

            # ✅ Normalize twitterScore for progress bar display
            scores = [float(row.get("twitterScore") or 0) for row in main_data if str(row.get("twitterScore")).strip().lower() not in ["", "nan", "none"]]
            max_score = max(scores, default=100)

            for row in main_data:
                try:
                    raw_score = float(row.get("twitterScore") or 0)
                    row["normalizedScore"] = round((raw_score / max_score) * 100, 1) if max_score > 0 else 0
                except Exception:
                    row["normalizedScore"] = 0

            # ✅ Pagination — not inside the loop!
            per_page = int(request.GET.get("per_page", 20))
            paginator = Paginator(main_data, per_page)
            page_number = request.GET.get("page")
            funding_main_page = paginator.get_page(page_number)

        except Exception as e:
            print("Funding main data error:", e)
            funding_main_page = []

    return render(request, "funding_rounds/funding_rounds.html", {
    "overview": overview,
    "hot_rounds": hot_rounds,
    "digest": digest,
    "per_page": per_page,
    "funding_main_page": funding_main_page
})

def merge_hot_rounds(raw_data):
    merged = {}
    for item in raw_data:
        key = item["coinName"]
        if key not in merged:
            merged[key] = {
                "coinName": item["coinName"],
                "coinImage": item["coinImage"],
                "raise": item["raise"],
                "funds": []
            }
        # Avoid duplicate logos
        existing_logos = {f["logo"] for f in merged[key]["funds"]}
        for fund in item["funds"]:
            if fund["logo"] not in existing_logos:
                merged[key]["funds"].append(fund)
                existing_logos.add(fund["logo"])
    return list(merged.values())