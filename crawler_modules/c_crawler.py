import math
import os
import requests
from time import sleep
from random import randint
from crawler_modules.c_modules import Commons, get_envs
from crawler_modules.c_parser import parser_dummy_site, parser_naver_store


class Crawler(Commons):
    base_headers = {
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.110 Safari/537.36",
        "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
        "accept-language": "en-US;en;q=0.9",
        "accept-encoding": "gzip, deflate, br",
    }

    def __init__(self, type: str, query=None, items=None) -> None:
        '''
        query 및 items의 경우 특정 키워드 검색 등을 위해 일단 구성
        차후 개발 명세에 따로 수정 가능
        '''
        super().__init__()
        _envs = get_envs()
        self.page = 1
        self.type = type
        self.items = items
        self.query = query
        self.is_error = False
        self.url = _envs[type]["url"]
        self.params = _envs[type]["params"]
        self.parser = getattr(parser_naver_store, _envs[type]["parser"])

    def execute(self, keyword="keyword"):
        '''
        개별 parser에서 데이터 처리
        execute는 1 request로 한정 (다만 마우스 스크롤, next page가 있는 경우에는 별도 조치 필요)
        여러 개의 키워드 쿼리가 있는 경우 main.py에서 iterate 수행 
        '''
        DATA_PATH = os.path.dirname(os.path.realpath(__file__)) + "/data"
        parser = self.parser()

        # KEYWORD_INFO
        keyword_info_parsed = parser.get_keyword_info(keyword)
        self.json_save(f"{DATA_PATH}/keyword_info_parsed.json", keyword_info_parsed)

        # PRODUCTS
        products_raw = parser.get_products(keyword)
        self.json_save(f"{DATA_PATH}/products_raw.json", products_raw)
        products_parsed = parser.parse_products_raw(products_raw)
        self.json_save(f"{DATA_PATH}/products_parsed.json", products_parsed)

        # STORE_PRODUCT_REVIEWS
        total_store_reviews, store_product_reviews_raw = parser.get_store_product_reviews()
        self.json_save(f"{DATA_PATH}/store_product_reviews_raw.json", store_product_reviews_raw)
        store_reviews_parsed = parser.parse_store_product_reviews_raw(store_product_reviews_raw)
        self.json_save(f"{DATA_PATH}/parse_store_product_reviews_raw.json", store_reviews_parsed)

        # INTEGRATED_PRODUCTS
        product_ids = [p["productId"] for p in products_parsed if p.get("lowMallList")]
        integrated_products_raw = parser.get_integrated_products(product_ids[0])
        self.json_save(f"{DATA_PATH}/integrated_products_raw.json", integrated_products_raw)
        integrated_products_parsed = parser.parse_integrated_products_raw(integrated_products_raw)
        self.json_save(f"{DATA_PATH}/integrated_products_parsed.json", integrated_products_parsed)
        
        # INTEGRATED_REVIEWS
        product_ids = [p["productId"] for p in products_parsed if p.get("lowMallList")]
        integrated_reviews_raw = parser.get_integrated_reviews(product_ids[0])
        self.json_save(f"{DATA_PATH}/integrated_reviews_raw.json", integrated_reviews_raw)
        integrated_reviews_parsed = parser.parse_integrated_reviews_raw(integrated_reviews_raw)
        self.json_save(f"{DATA_PATH}/integrated_reviews_parsed.json", integrated_reviews_parsed)
        pass

    def set_params(self):
        '''
        데이터 소스에서 필요한 parameter 정리
        기본적으로 제공해야 하는 cookie, 이외에도 args로 입력받은 내용을 정리
        '''
        self.params = []
        pass

    def request_html(self):
        self.set_params()
        try:
            urls = self.url_encoder(self.url, self.params)
            resp = requests.get(urls, headers=self.base_headers)
            resp.raise_for_status()
            print(f"[crawler log] executing {urls}...")
            return resp
        except Exception as e:
            self.is_error = True
            print(f"[crawler error log] {e}")
