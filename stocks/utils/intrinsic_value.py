import yfinance as yf
import pandas as pd
from scrapy import crawler
from ..models import Stock, DiscountedCashflowData
from .web_scraper import FinVizSpider
from collections import OrderedDict


def get_intrinsic_values(stock_symbols: list[str]):
    intrinsic_values = []

    for symbol in stock_symbols:
        symbol = validate_stock_symbol(symbol)
        if not symbol:
            intrinsic_values.append(None)
            continue

        # TODO: Optimize db hits
        try:
            stock = Stock.objects.get(symbol=symbol)
        except Stock.DoesNotExist:
            stock = Stock()
            stock.symbol = symbol
            stock.company_name = ticker.info["shortName"]
            stock.save()

        ticker = yf.Ticker(symbol)
        balance_sheet = ticker.balance_sheet.iloc[:, 0]
        cashflow_statement = ticker.cashflow.iloc[:, 0]
        latest_report_date: pd.Timestamp = ticker.income_stmt.columns[0]

        # TODO: Optimize db hits
        try:
            discounted_cashflow = stock.discountedcashflowdata_set.get(
                stated_at=latest_report_date.date()
            )
        except DiscountedCashflowData.DoesNotExist:
            discounted_cashflow = DiscountedCashflowData()
            discounted_cashflow.stock = stock
            discounted_cashflow.stated_at = latest_report_date.date()

            discounted_cashflow.operating_cashflow = cashflow_statement[
                "Operating Cash Flow"
            ]
            discounted_cashflow.total_debt = balance_sheet["Total Debt"]
            if "Cash Cash Equivalents And Short Term Investments" in balance_sheet:
                discounted_cashflow.cash_and_shortterm_investment = balance_sheet[
                    "Cash Cash Equivalents And Short Term Investments"
                ]
            elif (
                "Cash And Cash Equivalents" in balance_sheet
                and "Other Short Term Investments" in balance_sheet
            ):
                discounted_cashflow.cash_and_shortterm_investment = (
                    balance_sheet["Cash And Cash Equivalents"]
                    + balance_sheet["Other Short Term Investments"]
                )
            discounted_cashflow.beta = ticker.info["beta"]
            discounted_cashflow.shares_outstanding = ticker.info["sharesOutstanding"]

            process = crawler.CrawlerProcess(settings={"LOG_ENABLED": False})
            process.crawl(FinVizSpider, symbol, discounted_cashflow)
            process.start()

            discounted_cashflow.intrinsic_value = calc_discounted_cashflow(
                operating_cashflow=discounted_cashflow.operating_cashflow,
                total_debt=discounted_cashflow.total_debt,
                cash=discounted_cashflow.cash_and_shortterm_investment,
                growth_1_3=discounted_cashflow.eps_growth_projection_5y,
                growth_4_10=discounted_cashflow.eps_growth_projection_5y,
                beta=discounted_cashflow.beta,
                shares_outstanding=discounted_cashflow.shares_outstanding,
            )

            discounted_cashflow.save()

        intrinsic_values.append(discounted_cashflow)

    return intrinsic_values


def validate_stock_symbol(stock_symbol: str) -> str | None:
    """
    TODO
    Clean input to avoid injection attacks, and make sure
    this is a valid symbol.
    """
    return stock_symbol.upper()


def calc_discounted_cashflow(
    operating_cashflow: float,
    total_debt: float,
    cash: float,
    growth_1_3: float,
    growth_4_10: float,
    beta: float,
    shares_outstanding: float,
    max_growth=0.15,
) -> float:
    discount_rate = get_discount_rate_from_beta(beta)

    total_cashflow = 0

    prev_cashflow = operating_cashflow
    prev_discount_factor = 1

    for i in range(10):
        growth_rate = growth_1_3 if i < 3 else min(growth_4_10, max_growth)
        future_cashflow = prev_cashflow * (1 + growth_rate)
        future_discount_factor = prev_discount_factor * (1 - discount_rate)

        total_cashflow += future_cashflow * future_discount_factor

        prev_cashflow = future_cashflow
        prev_discount_factor = future_discount_factor

    intrinsic_value = (total_cashflow + cash - total_debt) / shares_outstanding

    return intrinsic_value


def get_discount_rate_from_beta(beta: float) -> float:
    if beta <= 0.8:
        return 0.050
    if beta >= 1.6:
        return 0.090

    beta_mapping = OrderedDict()
    beta_mapping[0.8] = 0.050
    beta_mapping[0.9] = 0.055
    beta_mapping[1.0] = 0.060
    beta_mapping[1.1] = 0.065
    beta_mapping[1.2] = 0.070
    beta_mapping[1.3] = 0.075
    beta_mapping[1.4] = 0.080
    beta_mapping[1.5] = 0.085
    beta_mapping[1.6] = 0.090

    lower_beta = 0.8
    upper_beta = 0.8
    for beta_val in beta_mapping.keys():
        if beta_val > beta:
            upper_beta = beta_val
            break
        lower_beta = beta_val

    if beta - lower_beta <= upper_beta - beta:
        return beta_mapping[lower_beta]
    else:
        return beta_mapping[upper_beta]


def test_get_discount_rate_from_beta():
    assert get_discount_rate_from_beta(0.7) == 0.050
    assert get_discount_rate_from_beta(0.8) == 0.050
    assert get_discount_rate_from_beta(0.83) == 0.050
    assert get_discount_rate_from_beta(0.87) == 0.055
    assert get_discount_rate_from_beta(0.9) == 0.055
    assert get_discount_rate_from_beta(0.93) == 0.055
    assert get_discount_rate_from_beta(0.97) == 0.060
    assert get_discount_rate_from_beta(1.0) == 0.060
    assert get_discount_rate_from_beta(1.03) == 0.060
    assert get_discount_rate_from_beta(1.07) == 0.065
    assert get_discount_rate_from_beta(1.1) == 0.065
    assert get_discount_rate_from_beta(1.5) == 0.085
    assert get_discount_rate_from_beta(1.53) == 0.085
    assert get_discount_rate_from_beta(1.57) == 0.09
    assert get_discount_rate_from_beta(1.6) == 0.09
    assert get_discount_rate_from_beta(1.7) == 0.09


if __name__ == "__main__":
    test_get_discount_rate_from_beta()
