from datetime import date
from pathlib import Path
import json
import os

import scrapy
from symbol_list import symbols


class FinVizSpider(scrapy.Spider):
    name = "finviz_spider"
    custom_settings = {
        "USER_AGENT": "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/34.0.1847.131 Safari/537.36"
    }

    _current_symbol_index = 0
    _current_date = None

    def __init__(self, *args, **kwargs):
        super(FinVizSpider, self).__init__(*args, **kwargs)
        url = self._get_current_url()
        self.start_urls = [url] if url else []
        self._data = self._read_data_from_json()

    def parse(self, response):
        stat_name_1 = response.css(
            "table.js-snapshot-table tr:nth-child(5) td:nth-child(5)::text"
        ).get()
        stat_name_2 = response.css(
            "table.js-snapshot-table tr:nth-child(6) td:nth-child(5)::text"
        ).get()
        # Guard against changing layout, which may lead to wrong number
        if stat_name_1 != "EPS next Y" or stat_name_2 != "EPS next 5Y":
            raise Exception("FinViz table layout has changed.")
        stat_value_1 = response.css(
            "table.js-snapshot-table tr:nth-child(5) td:nth-child(6) b::text"
        ).get()
        stat_value_2 = response.css(
            "table.js-snapshot-table tr:nth-child(6) td:nth-child(6) b::text"
        ).get()
        additional_data = {
            "eps_growth_projection_1y": stat_value_1,
            "eps_growth_projection_5y": stat_value_2,
        }

        current_symbol = self._get_current_symbol()
        # Guard against index overflow
        if not current_symbol:
            return
        self._data[current_symbol] = {
            **self._data.get(current_symbol, {}),
            **additional_data,
        }

        self._next_symbol()
        next_url = self._get_current_url()
        if next_url:
            yield response.follow(next_url, self.parse)
        else:
            self._write_data_to_json()

    def _get_current_url(self):
        current_symbol = self._get_current_symbol()
        if current_symbol:
            return f"https://finviz.com/quote.ashx?t={current_symbol}&p=d"
        else:
            return None

    def _get_current_symbol(self):
        if self._current_symbol_index < len(symbols):
            return symbols[self._current_symbol_index]
        else:
            return None

    def _next_symbol(self):
        self._current_symbol_index += 1

    def _read_data_from_json(self) -> dict[str, dict]:
        filename = self._get_json_file_path()
        try:
            with open(filename, "r", encoding="utf-8") as file:
                return json.load(file)
        except FileNotFoundError:
            return {}

    def _write_data_to_json(self):
        filename = self._get_json_file_path()
        os.makedirs(os.path.dirname(filename), exist_ok=True)
        with open(filename, "w", encoding="utf-8") as file:
            json.dump(self._data, file, ensure_ascii=True, indent=4)

    def _get_json_file_path(self):
        if not self._current_date:
            self._current_date = date.today()
        this_file_path = os.path.dirname(__file__)
        app_root_path = Path(this_file_path).parents[0]
        json_file_path = os.path.join(app_root_path, f"data/{self._current_date}.json")
        return json_file_path
