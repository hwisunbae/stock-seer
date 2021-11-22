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