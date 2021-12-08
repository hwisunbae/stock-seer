from django.db.models import Count
from django.test import TestCase
from .models import Tweets


class FunctionalityTestCase(TestCase):
    # def setUp(self):
    #     Animal.objects.create(name="lion", sound="roar")
    #     Animal.objects.create(name="cat", sound="meow")

    def check_tweet_num(self):
        """Animals that can speak are correctly identified"""
        print('hi')
        tweet_all = Tweets.objects.all().annotate(Count("id"))
        print(tweet_all)
        # self.assertEqual(tweet_all, 'The lion says "roar"')
        # self.assertEqual(cat.speak(), 'The cat says "meow"')
