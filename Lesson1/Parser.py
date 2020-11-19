import json
import requests


class Parse5Ka:

    url_categories = "https://5ka.ru/api/v2/categories/"
    url_special_offers = "https://5ka.ru/api/v2/special_offers/"
    params = { "records_per_page": 100, "page": 1, "categories": None }
        
    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.16; rv:82.0) Gecko/20100101 Firefox/82.0",
    }

    def __init__(self, save_path):
        self.save_path = save_path        
        
    def _get_data(self, url, params={}):
        response : requests.Response = requests.get(url, params=params, headers=self.headers)
        return response.json()

    def parse(self):
        data = self.parse_categories()

    def parse_categories(self):
        
        data_categories = self._get_data(self.url_categories)
        
        self.save_data(f'categories.json', data_categories)

        for category in data_categories:
            
            code = category.get("parent_group_code")

            current_params = self.params.copy()
            current_params["categories"] = code

            data_offers = self.parse_offers(current_params)

            category["products"] = data_offers

            self.save_data(f'{self.save_path}/{code}.json', category)

    def parse_offers(self, params):
        url = self.url_special_offers

        results = []

        while url:            
            data = self._get_data(url, params)
            
            url = data.get('next')
            
            if params:
                params = {}
            
            result = data.get('results', [])
            results.extend(result)
            
        return results

    def save_data(self, path, data: dict):        
        with open(path, 'w', encoding='UTF-8') as file:
            json.dump(data, file, ensure_ascii=False)


if __name__ == '__main__':    
    parser = Parse5Ka("categories")
    parser.parse()
