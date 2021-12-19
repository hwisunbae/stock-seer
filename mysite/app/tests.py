from django.contrib.auth.models import User
from django.contrib.staticfiles.testing import StaticLiveServerTestCase

from django.test import TestCase
from app.models import Tweets, Portfolio, Stock
import random
import string
import time

from selenium import webdriver
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import TimeoutException
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.by import By

print('Testing...')


# https://developer.mozilla.org/en-US/docs/Learn/Server-side/Django/Testing


# class TweetModelTests(TestCase):
#     def test_was_the_number_of_tweet_matching(self):
#         """
#         was_published_recently() returns False for questions whose pub_date
#         is in the future.
#         """
#         tweet_count = Tweets.objects.all().count()
#         self.assertIs(tweet_count, 4230)

def random_char(char_num):
    return ''.join(random.choice(string.ascii_letters) for _ in range(char_num))


def check_exists_by_xpath(webdriver, xpath):
    try:
        webdriver.find_element_by_xpath(xpath)
    except NoSuchElementException:
        return False
    return True


def check_count_by_xpath(webdriver, xpath):
    count = len(webdriver.find_elements_by_xpath(xpath))
    return count


class MySeleniumTests(StaticLiveServerTestCase):
    # fixtures = ['user-data.json']
    random_id = random_char(6)
    random_email = random_char(7) + "@gmail.com"
    random_password = random_char(5)

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.selenium = webdriver.Chrome(executable_path="/usr/local/bin/chromedriver")
        cls.selenium.implicitly_wait(10)

    @classmethod
    def tearDownClass(cls):
        cls.selenium.quit()
        super().tearDownClass()

    def test_create_account(self):
        print('test_create_account is executing...')
        """
        Test user object is created after create an account
        """
        response = self.client.get('/')
        # Check that the response is redirected.
        self.assertEqual(response.status_code, 302)

        self.selenium.get('%s%s' % (self.live_server_url, '/'))
        self.selenium.find_element_by_xpath('//a[text()="Create an Account!"]').click()
        self.selenium.find_element_by_id("exampleUserName").send_keys(self.random_id)
        self.selenium.find_element_by_id("exampleFirstName").send_keys('testFirstName')
        self.selenium.find_element_by_id("exampleLastName").send_keys('testLastName')
        self.selenium.find_element_by_id("exampleInputEmail").send_keys(self.random_email)
        self.selenium.find_element_by_id("exampleInputPassword").send_keys(self.random_password)
        self.selenium.find_element_by_xpath('//a[@value="Submit"]').click()

        # Check if alert appears
        WebDriverWait(self.selenium, 3).until(EC.alert_is_present(),
                                              'Timed out waiting for user object creation.')
        alert = self.selenium.switch_to.alert
        alert.accept()
        print("alert accepted")

        isUserCreated = User.objects.filter(email=self.random_email).count()
        # Check if user obj is created
        self.assertIs(isUserCreated, 1)

    def test_login(self):
        print('test_login is executing...')
        self.selenium.get('%s%s' % (self.live_server_url, '/'))

        response = self.client.get('/')
        # Check that the response is redirected.
        self.assertEqual(response.status_code, 302)

        self.selenium.find_element_by_id("exampleInputUsername").send_keys(self.random_email)
        self.selenium.find_element_by_id("exampleInputPassword").send_keys(self.random_password)
        self.selenium.find_element_by_xpath('//button[@type="submit"]').click()

        time.sleep(2)
        response = self.client.get('/')
        # Check that the response is 200 OK.
        self.assertTemplateUsed('index.html')

    def test_daterange(self):
        print('test_daterange is executing...')
        # Date only should be in 2021/05/01 - 2021/09/30
        print('Selecting 2021/03/01 - 2021/04/30')
        self.selenium.find_element_by_xpath('//input[@name="daterange"]').clear()
        self.selenium.find_element_by_xpath('//input[@name="daterange"]').send_keys('2021/03/01 - 2021/04/30')
        self.selenium.find_element_by_xpath('//button[@id="fetch-tweets"]').click()
        # Check if alert appears
        try:
            WebDriverWait(self.selenium, 3).until(EC.alert_is_present(),
                                                  'Timed out waiting for daterange picker')
            alert = self.selenium.switch_to.alert
            alert.accept()
            print("alert accepted")
        except TimeoutException:
            print("no alert")

        # Date only should be in 2021/05/01 - 2021/09/30
        print('2021/06/19 - 2021/07/28')
        self.selenium.refresh()
        time.sleep(5)

        self.selenium.find_element_by_xpath('//input[@name="daterange"]').clear()
        self.selenium.find_element_by_xpath('//input[@name="daterange"]').send_keys('2021/06/19 - 2021/07/28')
        self.selenium.find_element_by_xpath('//button[@id="fetch-tweets"]').click()
        WebDriverWait(self.selenium, 3).until(EC.presence_of_element_located((By.ID, 'finance-chart')))

    def test_index(self):
        print('test_index is executing...')

        # # check chartjs
        # xpath_chartjs = '//canvas[@class="chartjs-render-monitor"]'
        # print(check_exists_by_xpath(self.selenium, xpath_chartjs))
        # # check if canvas count is 3
        # print(True if check_count_by_xpath(self.selenium, xpath_chartjs) == 3 else False)

        # check portfolio
        rf_profit = self.selenium.find_element_by_xpath('//div[@id="rf-profit"]').text
        print(True if rf_profit == '$0' else False)

        xgb_profit = self.selenium.find_element_by_xpath('//div[@id="xgb-profit"]').text
        print(True if xgb_profit == '$0' else False)

        # # check table
        # response = self.client.get('/')
        # self.assertContains(response, 'No data available in table', status_code=302)

    def test_logout(self):
        time.sleep(5)
        self.selenium.find_element_by_xpath('//a[@id="userDropdown"]').click()
        self.selenium.find_element_by_xpath('//a[@data-target="#logoutModal"]').click()
        self.selenium.find_element_by_xpath('//div[@class="modal-footer"]//a[text()="Logout"]').click()
        self.assertTemplateUsed('login.html')

    def test_from_user_side(self):
        self.test_create_account()
        self.test_login()
        self.test_daterange()
        self.test_index()
        self.test_logout()
