from enum import Enum

from django.db import models


# Create your models here.
class Stock(models.Model):
    id = models.AutoField(primary_key=True)
    date = models.DateField()
    adj_close = models.DecimalField(max_digits=20, decimal_places=17)
    close = models.DecimalField(max_digits=20, decimal_places=17)
    volume = models.DecimalField(max_digits=10, decimal_places=0)

    def __str__(self):
        return str(self.date)


class Tweets(models.Model):
    id = models.DecimalField(max_digits=19, decimal_places=0)
    created_at = models.DateTimeField()
    user_name = models.CharField(max_length=300)
    text = models.CharField(max_length=400)
    lang = models.CharField(max_length=5)
    tokens = models.CharField(max_length=300)
    subjectivity = models.DecimalField(max_digits=3, decimal_places=3)
    polarity = models.DecimalField(max_digits=3, decimal_places=3)
    analysis = models.DecimalField(max_digits=2, decimal_places=0)
    _id = models.AutoField(primary_key=True)

    def __str__(self):
        return str(self.id)


class MLMethod(Enum):
    RF = 'RandomForest'
    XG = 'XGBoost'


class Decision(Enum):
    B = 'Buy'
    S = 'Sell'


class Portfolio(models.Model):
    id = models.AutoField(primary_key=True)

    ml_method = models.CharField(
        max_length=20,
        choices=[(tag, tag.value) for tag in MLMethod]
    )

    decision = models.CharField(
        max_length=20,
        choices=[(tag, tag.value) for tag in Decision]
    )

    date = models.DateTimeField()
    price = models.DecimalField(max_digits=20, decimal_places=3)
    profit = models.DecimalField(max_digits=20, decimal_places=3)
