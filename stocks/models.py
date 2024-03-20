from django.db import models


class Stock(models.Model):
    symbol = models.CharField(max_length=10)
    company_name = models.CharField(max_length=100)

    def __str__(self) -> str:
        return self.symbol


class DiscountedCashflowData(models.Model):
    stock = models.ForeignKey(Stock, on_delete=models.CASCADE)

    operating_cashflow = models.BigIntegerField()
    total_debt = models.BigIntegerField()
    cash_and_shortterm_investment = models.BigIntegerField()
    eps_growth_projection_1y = models.FloatField()
    eps_growth_projection_5y = models.FloatField()
    beta = models.FloatField()
    shares_outstanding = models.BigIntegerField()
    stated_at = models.DateField("date of the financial statements")
    intrinsic_value = models.FloatField()

    def __str__(self) -> str:
        return f"{self.stock.symbol} ({self.stated_at})"
