from django.shortcuts import render

from .models import Stock


default_symbols = ["MSFT", "AAPL"]


def index(request):
    stocks = Stock.objects.filter(symbol=default_symbols)
    context = {
        "stocks": stocks,
    }
    return render(request, "stocks/index.html", context)
