import json
from urllib import parse
from datetime import datetime

crawler_variables = {
    "dummy_site": {
        "url": "https://www.dummysite.com/search?",
        "params": [],
        "parser": "parser_dummy"
    },
    "naver_store_keyword_info":{
        "url": "https://search.shopping.naver.com/search/all?",
        "params": {"query": "남성 스니커즈"},
        "parser": "NaverShoppingCrawler"
    },
    "naver_store_products":{
        "url": "https://search.shopping.naver.com/search/all?",
        "params": {
                "query": "남성 스니커즈",
                "cat_id": "",
                "frm": ""
            },
        "parser": "NaverShoppingCrawler"
    },
    "naver_store_product_reviews":{
        "url": "https://m.shopping.naver.com/v1/reviews/paged-reviews",
        "params": {
            "pageSize": 20,
            "merchantNo": "500245685",
            "originProductNo": 4662556695,
            "sortType": "REVIEW_RANKING"
        },
        "parser": "NaverShoppingCrawler"
    },
    "naver_store_integrated_products":{
        "url": "https://search.shopping.naver.com/catalog/",
        "parser": "NaverShoppingCrawler"
    },
    "naver_store_integrated_reviews":{
        "url": "https://search.shopping.naver.com/api/review?",
        "params": {
            "isNeedAggregation": "N",
            "pageSize":20,
            "sortType":"QUALITY",
        },
        "parser": "NaverShoppingCrawler"
    },
    "instagram": {
        "url": "",
        "params": [],
        "parser": "parser_instagram"
    },
    "tictoc": {
        "url": "https://www.tiktok.com/",
        "params": [],
        "parser": "parser_tictoc"
    },
}

def get_envs():
    return crawler_variables

class Commons:
    def __init__(self) -> None:
        self.time_s = datetime.now()
        self.time_n = self.time_s.strftime("%Y%m%d%H%M")

    def url_encoder(self, url: str, param: object):
        return url + parse.urlencode(param)

    def cal_time(self):
        return  datetime.now() - self.time_s

    def json_load(self, file_path: str):
        file = open(file_path, 'rt', encoding='UTF8')
        return json.load(file)

    def json_save(self, file_path: str, datas: object):
        file = open(file_path, "w", encoding='utf-8')
        return json.dump(datas, file, ensure_ascii=False)
