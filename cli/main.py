import os
import typer
from scrapy.crawler import CrawlerProcess

from common.io_handler.file_io import FileIO
from common.data_fetcher.web_scraper import FinVizSpider
from common.data_fetcher.yahoo_finance import YahooFinanceFetcher
from common.calculator.intrinsic_value import (
    calc_discounted_cashflow,
    get_discount_rate_from_beta,
)


def main(symbols: str):
    symbol_list = [symbol.upper() for symbol in symbols.split(",")]
    data_dir_path = os.path.join(os.path.dirname(__file__), "data")
    file_io = FileIO(data_dir_path)

    # Fetch data from FinViz
    process = CrawlerProcess(settings={"LOG_ENABLED": False})
    process.crawl(FinVizSpider, symbol_list, file_io)
    process.start()

    # Fetch data from Yahoo Finance
    yf_fetcher = YahooFinanceFetcher(symbol_list, file_io)
    yf_fetcher.execute()

    # Calculate intrinsic value
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
        print(f"{symbol}: {intrinsic_value}")


if __name__ == "__main__":
    typer.run(main)
