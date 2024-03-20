from django.shortcuts import render

from .models import Stock
from .utils import intrinsic_value


default_symbols = ["MSFT", "AAPL"]


def index(request):
    intrinsic_value_data = intrinsic_value.get_intrinsic_values(default_symbols)
    context = {
        "intrinsic_value_data": intrinsic_value_data,
    }
    return render(request, "stocks/index.html", context)
