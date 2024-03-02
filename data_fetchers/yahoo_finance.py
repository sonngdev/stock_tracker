from datetime import date
from pathlib import Path
import json
import os

import yfinance as yf
from symbol_list import symbols


class YahooFinanceFetcher:
    _current_symbol_index = 0
    _current_date = None

    def __init__(self):
        self._data = self._read_data_from_json()

    def execute(self):
        current_symbol = self._get_current_symbol()

        while current_symbol:
            ticker = yf.Ticker(current_symbol)

            company_name = ticker.info["shortName"]
            operating_cash_flow = ticker.cash_flow.iloc[:, 0]["Operating Cash Flow"]
            net_income = ticker.income_stmt.iloc[:, 0]["Net Income"]
            total_debt = ticker.balance_sheet.iloc[:, 0]["Total Debt"]
            cash_and_short_term_investment = ticker.balance_sheet.iloc[:, 0]["Cash Cash Equivalents And Short Term Investments"]
            num_shares_outstanding = ticker.info["sharesOutstanding"]
            beta = ticker.info["beta"]
            additional_data = {
                "symbol": current_symbol,
                "company_name": company_name,
                "operating_cash_flow": operating_cash_flow,
                "net_income": net_income,
                "total_debt": total_debt,
                "cash_and_short_term_investment": cash_and_short_term_investment,
                "num_shares_outstanding": num_shares_outstanding,
                "beta": beta,
            }

            self._data[current_symbol] = {
                **self._data.get(current_symbol, {}),
                **additional_data,
            }

            self._next_symbol()
            current_symbol = self._get_current_symbol()

        self._write_data_to_json()

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


if __name__ == '__main__':
    fetcher = YahooFinanceFetcher()
    fetcher.execute()
