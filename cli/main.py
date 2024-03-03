import os
import typer
import datetime

from scrapy.crawler import CrawlerProcess
from common.io_handler.file_io import FileIO
from common.data_fetcher.web_scraper import FinVizSpider
from common.data_fetcher.yahoo_finance import YahooFinanceFetcher
from common.calculator.intrinsic_value import (
    calc_discounted_cashflow,
    get_discount_rate_from_beta,
)
from common.formatter import stat_formatter
from rich.console import Console
from rich.table import Table

console = Console()


def main(symbols: str):
    symbol_list = [symbol.upper() for symbol in symbols.split(",")]
    data_dir_path = os.path.join(os.path.dirname(__file__), "data")
    current_date = datetime.date.today()
    file_io = FileIO(data_dir_path, current_date)

    if not file_io.exist(current_date):
        # Fetch data from FinViz
        process = CrawlerProcess(settings={"LOG_ENABLED": False})
        process.crawl(FinVizSpider, symbol_list, file_io)
        process.start()

        # Fetch data from Yahoo Finance
        yf_fetcher = YahooFinanceFetcher(symbol_list, file_io)
        yf_fetcher.execute()

    # Calculate intrinsic value
    table = Table()
    table.add_column("Symbol")
    table.add_column("Cash Flow (mil)", justify="right")
    table.add_column("Debt (mil)", justify="right")
    table.add_column("Cash (mil)", justify="right")
    table.add_column("Growth (%)", justify="right")
    table.add_column("Discount rate (%)", justify="right")
    table.add_column("Shares", justify="right")
    table.add_column("Intrinsic value", justify="right")

    data = file_io.read()
    for symbol, stats in data.items():
        discount_rate = get_discount_rate_from_beta(stats["beta"])
        intrinsic_value = calc_discounted_cashflow(
            operating_cashflow=stats["operating_cashflow"],
            total_debt=stats["total_debt"],
            cash=stats["cash_and_short_term_investment"],
            growth_1_3=stats["eps_growth_projection_5y"],
            growth_4_10=stats["eps_growth_projection_5y"],
            discount_rate=discount_rate,
            shares_outstanding=stats["num_shares_outstanding"],
        )
        table.add_row(
            symbol,
            stat_formatter.display_million(stats["operating_cashflow"]),
            stat_formatter.display_million(stats["total_debt"]),
            stat_formatter.display_million(stats["cash_and_short_term_investment"]),
            stat_formatter.display_percentage(stats["eps_growth_projection_5y"]),
            stat_formatter.display_percentage(discount_rate),
            stat_formatter.add_thousand_separation(stats["num_shares_outstanding"]),
            stat_formatter.limit_2_decimal_points(intrinsic_value),
        )

    console.print(table)


if __name__ == "__main__":
    typer.run(main)
