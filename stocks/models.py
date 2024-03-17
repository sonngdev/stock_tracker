from django.db import models


class FetchedData(models.Model):
    symbol = models.CharField(max_length=10)
    cash_flow = models.BigIntegerField()
    total_debt = models.BigIntegerField()
    cash = models.BigIntegerField()
    growth_1_3 = models.FloatField()
    growth_4_10 = models.FloatField()
    beta = models.FloatField()
    shares_outstanding = models.BigIntegerField()
    stated_at = models.DateField("date of the financial statements")

    def __str__(self) -> str:
        return f"{self.symbol} ({self.stated_at})"
