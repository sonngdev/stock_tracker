import yfinance as yf
from common.io_handler.io_handler import IOHandler


class YahooFinanceFetcher:
    _current_symbol_index = 0
    _current_date = None

    def __init__(self, symbols: list[str], io_handler: IOHandler):
        self._symbols = symbols
        self._io_handler = io_handler
        self._data = self._io_handler.read()

    def execute(self):
        current_symbol = self._get_current_symbol()

        while current_symbol:
            ticker = yf.Ticker(current_symbol)

            company_name = ticker.info["shortName"]
            operating_cashflow = ticker.cashflow.iloc[:, 0]["Operating Cash Flow"]
            net_income = ticker.income_stmt.iloc[:, 0]["Net Income"]
            total_debt = ticker.balance_sheet.iloc[:, 0]["Total Debt"]
            cash_and_short_term_investment = ticker.balance_sheet.iloc[:, 0][
                "Cash Cash Equivalents And Short Term Investments"
            ]
            num_shares_outstanding = ticker.info["sharesOutstanding"]
            beta = ticker.info["beta"]
            additional_data = {
                "symbol": current_symbol,
                "company_name": company_name,
                "operating_cashflow": operating_cashflow,
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

        self._io_handler.write(self._data)

    def _get_current_symbol(self):
        if self._current_symbol_index < len(self._symbols):
            return self._symbols[self._current_symbol_index]
        else:
            return None

    def _next_symbol(self):
        self._current_symbol_index += 1


if __name__ == "__main__":
    fetcher = YahooFinanceFetcher()
    fetcher.execute()
