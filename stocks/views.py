from django.shortcuts import render

from .models import DiscountedCashflowData
from .utils import intrinsic_value, stat_formatter
import yfinance as yf


default_symbols = ["MSFT", "AAPL"]


def index(request):
    intrinsic_value_data = intrinsic_value.get_intrinsic_values(default_symbols)
    table_items = [IndexItem(data) for data in intrinsic_value_data]
    context = {
        "table_items": table_items,
    }
    return render(request, "stocks/index.html", context)


class IndexItem:
    def __init__(self, intrinsic_value_data) -> None:
        self.stock_symbol = intrinsic_value_data.stock.symbol
        self.latest_report_date = intrinsic_value_data.stated_at
        self.intrinsic_value = stat_formatter.limit_2_decimal_points(
            intrinsic_value_data.intrinsic_value
        )

        ticker = yf.Ticker(self.stock_symbol)
        current_price = ticker.info["currentPrice"]
        self.current_price = stat_formatter.limit_2_decimal_points(current_price)
        self.should_buy = intrinsic_value_data.intrinsic_value > current_price


class TableSummaryItem:
    def __init__(self, intrinsic_value_data: DiscountedCashflowData) -> None:
        self.stock_symbol = intrinsic_value_data.stock.symbol
        self.operating_cashflow = stat_formatter.display_million(
            intrinsic_value_data.operating_cashflow
        )
        self.total_debt = stat_formatter.display_million(
            intrinsic_value_data.total_debt
        )
        self.cash_and_shortterm_investment = stat_formatter.display_million(
            intrinsic_value_data.cash_and_shortterm_investment
        )
        self.eps_growth_projection_5y = stat_formatter.display_percentage(
            intrinsic_value_data.eps_growth_projection_5y
        )
        self.beta = intrinsic_value_data.beta
        self.shares_outstanding = stat_formatter.add_thousand_separation(
            intrinsic_value_data.shares_outstanding
        )
        self.intrinsic_value = stat_formatter.limit_2_decimal_points(
            intrinsic_value_data.intrinsic_value
        )

        ticker = yf.Ticker(self.stock_symbol)
        current_price = ticker.info["currentPrice"]
        self.current_price = stat_formatter.limit_2_decimal_points(current_price)
        self.should_buy = (
            "YES" if intrinsic_value_data.intrinsic_value > current_price else "NO"
        )
