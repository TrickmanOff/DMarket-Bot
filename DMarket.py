import requests
from urllib.parse import urlencode
import json
import datetime
import statistics
import time
import random
import browser_cookie3
import pprint
from math import floor


class SalesHistory:
    st_url = 'https://api.dmarket.com/marketplace-api/v1/sales-history?'

    @staticmethod
    def make_request(session, title, game_id='a8db', period='1M', currency='USD'):
        data = {
            'Title': title,
            'GameID': game_id,
            'Period': period,
            'Currency': currency
        }
        url = SalesHistory.st_url + urlencode(data)
        return session.get(url).text

class Market:
    st_url = 'https://api.dmarket.com/exchange/v1/market/items?'

    @staticmethod
    def make_request(session, order_by='best_deals', order_dir='desc', title='', price_from=0, price_to=0, game_id='a8db', offset=0, limit=10, currency='USD',):
        data = {
            'orderBy': order_by,
            'orderDir': order_dir,
            'title': title,
            'priceFrom': price_from,
            'priceTo': price_to,
            'gameId': game_id,
            'offset': offset,
            'limit': limit,
            'currency': currency
        }
        url = Market.st_url + urlencode(data)
        return session.get(url).text

class LastSales:
    st_url = 'https://api.dmarket.com/marketplace-api/v1/last-sales?'

    @staticmethod
    def make_request(session, title, game_id='a8db', currency='USD'):
        data = {
            'Title': title,
            'GameID': game_id,
            'Currency': currency
        }
        url = LastSales.st_url + urlencode(data)
        return session.get(url).text

class DMarketApi:

    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.113 Safari/537.36'})
        self.apis = {
            'market': Market,
            'last_sales': LastSales,
            'sales_history': SalesHistory
        }
        self.market = Market()
        self.last_sales = LastSales()
        self.st_val = 1587427200
        self.st_date = datetime.date(2020, 4, 21)

    def get_cookies(self):
        cj = browser_cookie3.chrome(domain_name='dmarket.com')
        self.session.cookies = cj

    def make_request(self, api, **kwargs):
        """
        api: api, в котором делается запрос
        собирает запрос по переданным аргументам
        возвращает данные в python формате
        """
        #print("Making URL request...")
        time.sleep(0.5 + random.uniform(-0.1, 0.5))
        try:
            data = self.apis[api].make_request(session=self.session, **kwargs)
        except requests.exceptions:
            print("Error with URL request")
        else:
            return json.loads(data)

    def search_title(self, title, limit = 10):
        """
        data: результат запроса
        возвращает список items, в котором лежат вещи ТОЛЬКО с указанным title
        items возрастают по цене
        """
        data = self.make_request(api='market', title=title, limit=limit, order_by='price', order_dir='asc')

        return data['objects']

    def site_time(self, hours=48):
        """
        возвращает время hours часов назад на сайте
        """
        st_val = 1587497220
        st_date = datetime.datetime(2020, 4, 22, 5, 27, 0)

        delta = (datetime.datetime.now() - st_date).total_seconds() - hours * 60 * 60
        return int(st_val + delta)

    def avg_price(self, title):
        """
        возвращает среднюю цену на title за последние двое суток
        если продаж не было, то 1
        """
        data = self.make_request(api='last_sales', title=title)

        time = self.site_time()
        amounts = []
        for sale in data['LastSales']:
            if int(sale['Date']) >= time:
                amounts.append(int(sale['Price']['Amount']))

        if len(amounts) <= 3:
            return 1
        return statistics.median(sorted(amounts)[:len(amounts)-2])

    def min_sell_price(self, title):
        cur_offers = self.search_title(title=title, limit=5)
        min_sell_price = 1e9
        if len(cur_offers) >= 5:
            min_sell_price = min(min_sell_price, int(cur_offers[4]['price']['USD']))

        return min_sell_price

    def sell_price(self, title):
        """
        :return: цену продажи указанной вещи
        """
        avg = self.avg_price(title=title)
        cur_offers = self.search_title(title=title, limit=1)
        min_sell_price = 1e9
        if len(cur_offers) > 0:
            min_sell_price = min(min_sell_price, int(cur_offers[0]['price']['USD']))

        return min(min_sell_price, avg)

    def get_new_orders(self, limit = 1, **kwargs):
        """
        возвращает список новых предложений
        """
        return self.make_request(api='market', order_by='updated', limit=limit, price_from=10, price_to=self.get_balance(), **kwargs)['objects']

    def get_balance(self):
        url = 'https://api.dmarket.com/account/v1/balance'
        data = json.loads(self.session.get(url).text)['usd']
        return int(data)

    def get_sales(self, title):
        """"
        :return возвращает кол-во проданных скинов в каждый день на протяжении месяца
        """
        return self.make_request(api='sales_history', title=title)['SalesHistory']

    def is_popular(self, title):
        """
        :return: возвращает True, если вещь регулярно продавали в течение месяца
        """
        sales = self.get_sales(title=title)
        return sorted(sales[:-1])[5] >= 3

    def month_sales(self, title):
        sales = self.get_sales(title=title)
        prices = []
        for price in sales['Prices'][22:]:
            if price != '':
                prices.append(float(price))

        return {
            'price': (0 if len(prices) == 0 else statistics.median(prices)),
            'is_popular': not len(sales['Items']) == 0 and sorted(sales['Items'][:-1])[5] >= 3
        }

    def get_optimal_price(self, title):
        """
        :param title:
        :return: возвращает dict(potential_sell_price, price_to_buy, is_popular)
        """
        month_sales = self.month_sales(title=title)

        # минимальная цена продажи
        sell_price = floor(min(self.min_sell_price(title=title), month_sales['price']))
        # продаём на 1% дешевле, но не менее, чем на 0.01
        sell_price = min(floor(0.99 * sell_price), sell_price - 1)
        # комиссия
        sell_price = floor(0.95 * sell_price)
        sell_price = int(sell_price)
        # такая цена покупки, чтобы выгода составили 3% от цены продажи, но минимум 0.02$
        buy_price = int(min(floor(sell_price / 1.03), sell_price - 2))
        return {
            'potential_sell_price': sell_price,
            'price_to_buy': buy_price,
            'is_popular': month_sales['is_popular']
        }

