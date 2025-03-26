import requests
from django.shortcuts import render
from django.http import JsonResponse
from django.conf import settings

CHAINALYSIS_API_KEY = settings.CHAINALYSIS_API_KEY
CHAINALYSIS_API_URL = "https://public.chainalysis.com/api/v1/address/"

def check_sanctions(request):
    """Renders the form and handles API requests."""
    if request.method == "POST":
        wallet_address = request.POST.get("wallet_address", "").strip()

        if not wallet_address:
            return JsonResponse({"error": "Please enter a wallet address"}, status=400)

        headers = {
            "X-API-Key": CHAINALYSIS_API_KEY,
            "Accept": "application/json"
        }

        response = requests.get(f"{CHAINALYSIS_API_URL}{wallet_address}", headers=headers)

        if response.status_code == 200:
            return JsonResponse(response.json(), safe=False)
        else:
            return JsonResponse({"error": "Failed to fetch data", "status_code": response.status_code}, status=response.status_code)

    return render(request, "sanctions/check_sanctions.html")
