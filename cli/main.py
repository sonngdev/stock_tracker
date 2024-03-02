import os
import typer
from scrapy.crawler import CrawlerProcess

from common.io_handler.file_io import FileIO
from common.data_fetchers.web_scraper import FinVizSpider
from common.data_fetchers.yahoo_finance import YahooFinanceFetcher


def main(symbols: str):
    symbol_list = symbols.split(",")
    data_dir_path = os.path.join(os.path.dirname(__file__), "data")
    file_io = FileIO(data_dir_path)

    # Fetch data from FinViz
    process = CrawlerProcess(settings={"LOG_ENABLED": False})
    process.crawl(FinVizSpider, symbol_list, file_io)
    process.start()

    # Fetch data from Yahoo Finance
    yf_fetcher = YahooFinanceFetcher(symbol_list, file_io)
    yf_fetcher.execute()


if __name__ == "__main__":
    typer.run(main)
