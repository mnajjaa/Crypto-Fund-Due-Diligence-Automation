#########################################################################
# Single fund page scraper
#########################################################################
import requests
import csv
import os
import time



####################Focus Area####################
# This module fetches focus area data from the CryptoRank API and saves it to CSV files.
BASE_URL = 'https://api.cryptorank.io/v0/coin-funds/focus-area/'
ALL_CSV_PATH = 'data/all_focus_areas.csv'


def get_csv_path(slug):
    return f'data/focus_area_{slug}.csv'


def fetch_focus_area_data(slug, save_individual=True, save_all=True):
    url = f"{BASE_URL}{slug}"
    try:
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            data = response.json().get("data", [])
            if save_individual:
                save_focus_area_to_csv(slug, data)
            if save_all:
                append_to_all_focus_area_csv(slug, data)
            return data
    except Exception as e:
        print(f"[ERROR] API fetch failed for {slug}: {e}")
    return None


def save_focus_area_to_csv(slug, data):
    path = get_csv_path(slug)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, mode='w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=["tag", "count", "percent"])
        writer.writeheader()
        for row in data:
            writer.writerow({
                "tag": row.get("tag", ""),
                "count": row.get("count", 0),
                "percent": row.get("percent", 0)
            })


def append_to_all_focus_area_csv(slug, data):
    os.makedirs(os.path.dirname(ALL_CSV_PATH), exist_ok=True)
    file_exists = os.path.isfile(ALL_CSV_PATH)

    with open(ALL_CSV_PATH, mode='a', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=["fund_slug", "tag", "count", "percent"])
        if not file_exists:
            writer.writeheader()
        for row in data:
            writer.writerow({
                "fund_slug": slug,
                "tag": row.get("tag", ""),
                "count": row.get("count", 0),
                "percent": row.get("percent", 0)
            })


def load_focus_area_from_csv(slug):
    path = get_csv_path(slug)
    data = []
    try:
        with open(path, mode='r', newline='', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                data.append({
                    "tag": row.get("tag", ""),
                    "count": int(row.get("count", 0)),
                    "percent": float(row.get("percent", 0))
                })
    except Exception as e:
        print(f"[ERROR] Reading CSV fallback for {slug} failed: {e}")
    return data


def bulk_fetch_focus_areas(slug_list):
    for slug in slug_list:
        print(f"[INFO] Fetching {slug} ...")
        fetch_focus_area_data(slug)
        time.sleep(0.5)  # optional rate limit

#########################End Focus Area####################

