import scrapy
from bs4 import BeautifulSoup
from ..models import DiscountedCashflowData


class FinVizSpider(scrapy.Spider):
    name = "finviz_spider"
    custom_settings = {
        "USER_AGENT": "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/34.0.1847.131 Safari/537.36"
    }

    def __init__(self, symbol: str, data_obj: DiscountedCashflowData, *args, **kwargs):
        super(FinVizSpider, self).__init__(*args, **kwargs)
        self.start_urls = [f"https://finviz.com/quote.ashx?t={symbol}&p=d"]
        self.data_obj = data_obj

    def parse(self, response):
        stat_name_1 = innertext(
            response.css("table.js-snapshot-table tr:nth-child(5) td:nth-child(5)")
        )
        stat_name_2 = innertext(
            response.css("table.js-snapshot-table tr:nth-child(6) td:nth-child(5)")
        )

        # Guard against changing FinViz table layout, which may lead to wrong number
        assert stat_name_1 == "EPS next Y" and stat_name_2 == "EPS next 5Y"

        stat_value_1 = innertext(
            response.css("table.js-snapshot-table tr:nth-child(5) td:nth-child(6)")
        )
        stat_value_2 = innertext(
            response.css("table.js-snapshot-table tr:nth-child(6) td:nth-child(6)")
        )

        self.data_obj.eps_growth_projection_1y = parse_percentage(stat_value_1)
        self.data_obj.eps_growth_projection_5y = parse_percentage(stat_value_2)


def innertext(selector):
    """
    Reference: https://github.com/ddikman/scrapy-innertext
    """
    html = selector.get()
    soup = BeautifulSoup(html, "html.parser")
    return soup.get_text().strip()


def parse_percentage(percentage: str) -> float:
    return float(percentage[:-1]) / 100
