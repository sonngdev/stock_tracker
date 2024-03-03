from collections import OrderedDict


def calc_discounted_cashflow(
    operating_cashflow: float,
    total_debt: float,
    cash: float,
    growth_1_3: float,
    growth_4_10: float,
    discount_rate: float,
    shares_outstanding: float,
    max_growth=0.15,
) -> float:
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
