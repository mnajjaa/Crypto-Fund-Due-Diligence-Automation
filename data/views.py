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
