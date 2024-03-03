def display_million(number: float) -> str:
    return add_thousand_separation(int(number / 1_000_000))


def display_percentage(number: float) -> str:
    return limit_2_decimal_points(number * 100)


def add_thousand_separation(number: int | float) -> str:
    return f"{number:,}"


def limit_2_decimal_points(number: float) -> str:
    return f"{number:.2f}"
