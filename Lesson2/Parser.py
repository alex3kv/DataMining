import os
import datetime as dt
import dotenv
import requests
from urllib.parse import urljoin
from bs4 import BeautifulSoup
import pymongo as pm

dotenv.load_dotenv('.env')
MONTHS = {
    "янв": 1,
    "фев": 2,
    "мар": 3,
    "апр": 4,
    "май": 5,
    "мая": 5,
    "июн": 6,
    "июл": 7,
    "авг": 8,
    "сен": 9,
    "окт": 10,
    "ноя": 11,
    "дек": 12,
}


class MagnitParser:

    def __init__(self, url):
        self.url = url
        db = pm.MongoClient(os.getenv('DATA_BASE'))
        self.db = db['parser']

    def _get(self, url: str) -> BeautifulSoup:        
        response = requests.get(url)
        return BeautifulSoup(response.text, 'lxml')

    def run(self):
        soup = self._get(self.url)
        for product in self.parse(soup):
            self.save(product)

    def parse(self, soup: BeautifulSoup) -> dict:
        catalog = soup.find('div', attrs={'class': 'сatalogue__main'})

        for product in catalog.findChildren('a'):
            try:
                result = self.get_product(product)
            except AttributeError:
                continue
            yield result

    def get_product(self, soup):
                
        result = {}
        
        result["url"] = urljoin(self.url, soup.attrs.get('href'))
        result["promo_name"] = soup.find('div', attrs={'class': 'card-sale__header'}).text
        result["product_name"] = soup.find('div', attrs={'class': 'card-sale__title'}).text
        result["old_price"] = float('.'.join(itm for itm in soup.find('div', attrs={'class': 'label__price_old'}).text.split()))
        result["new_price"] = float('.'.join(itm for itm in soup.find('div', attrs={'class': 'label__price_new'}).text.split()))
        result["image_url"] = urljoin(self.url, soup.find('img').attrs.get('data-src'))

        dt_parser = self.date_parse(soup.find('div', attrs={'class': 'card-sale__date'}).text)

        result["date_from"] = next(dt_parser)
        result["date_to"] = next(dt_parser)                   

        return result

    @staticmethod
    def date_parse(date_string: str):
        date_list = date_string.replace('с ', '', 1).replace('\n', '').split('до')
        for date in date_list:
            temp_date = date.split()
            yield dt.datetime(year=dt.datetime.now().year, day=int(temp_date[0]), month=MONTHS[temp_date[1][:3]])

    def save(self, data: dict):
        collection = self.db['magnit']
        collection.insert_one(data)


if __name__ == '__main__':
    parser = MagnitParser('https://magnit.ru/promo/?geo=moskva')
    parser.run()
