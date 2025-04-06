import requests
from django.shortcuts import render
from django.http import JsonResponse
from django.conf import settings
from .utils.moralis import get_wallet_token_balances, get_wallet_net_worth

CHAINALYSIS_API_KEY = settings.CHAINALYSIS_API_KEY
CHAINALYSIS_API_URL = "https://public.chainalysis.com/api/v1/address/"

def check_sanctions(request):
    """Renders the form and handles API requests."""
    if request.method == "POST":
        wallet_address = request.POST.get("wallet_address", "").strip()
        chain = request.POST.get("chain", "eth")  # 🆕 default to "eth" if not provided

        if not wallet_address:
            return JsonResponse({"error": "Please enter a wallet address"}, status=400)


        # Call Chainalysis
        headers = {
            "X-API-Key": CHAINALYSIS_API_KEY,
            "Accept": "application/json"
        }

        chainalysis_data = None
        response = requests.get(f"{CHAINALYSIS_API_URL}{wallet_address}", headers=headers)

        if response.status_code == 200:
            chainalysis_data = response.json()
        else:
            return JsonResponse({
                "error": "Failed to fetch sanctions data",
                "status_code": response.status_code
            }, status=response.status_code)

        # Moralis
        moralis_tokens = get_wallet_token_balances(wallet_address, chain)
        moralis_networth = get_wallet_net_worth(wallet_address, chain)

        return JsonResponse({
            "identifications": chainalysis_data.get("identifications", []),
            "moralis_tokens": moralis_tokens,
            "moralis_networth": moralis_networth
        }, safe=False)

    return render(request, "sanctions/check_sanctions.html")
