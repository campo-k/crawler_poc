import math
import os
import requests
from time import sleep
from random import randint
from crawler_modules.c_modules import Commons, get_envs
from crawler_modules.c_parser import parser_dummy_site, parser_naver_store
from bs4 import BeautifulSoup
import json


class Crawler(Commons):
    base_headers = {
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.110 Safari/537.36",
        "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
        "accept-language": "en-US;en;q=0.9",
        "accept-encoding": "gzip, deflate, br",
    }
    post_headers = {
        "accept": 'application/json, text/plain, */*',
        "accept-encoding": 'gzip, deflate, br',
        "accept-language": 'ko-KR,ko;q=0.9,zh-CN;q=0.8,zh;q=0.7,en-US;q=0.6,en;q=0.5',
        "content-type": 'application/json;charset=UTF-8',
        "user-agent": 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.0.0 Safari/537.36',
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
        self.params = _envs[type].get("params", {})
        self.parser = getattr(parser_naver_store, _envs[type]["parser"])

    def execute(self):
        '''
        개별 parser에서 데이터 처리
        execute는 1 request로 한정 (다만 마우스 스크롤, next page가 있는 경우에는 별도 조치 필요)
        여러 개의 키워드 쿼리가 있는 경우 main.py에서 iterate 수행 
        '''
        DATA_PATH = os.path.dirname(os.path.realpath(__file__)) + "/data"
        parser = self.parser()
        data_raw = None
        data_parsed = None

        if self.type == "naver_store_keyword_info":
            soup = self.request_bs4()
            data_parsed = parser.get_keyword_info(soup)
        elif self.type == "naver_store_products":
            data_raw = self.iter_pages(self.request_bs4, parser.get_products, page_param_name="pagingIndex")
            data_parsed = parser.parse_products_raw(data_raw)
        elif self.type == "naver_store_product_reviews":
            data_raw = self.iter_pages(self.request_post, parser.get_store_product_reviews, page_param_name="page")
            data_parsed = parser.parse_store_product_reviews_raw(data_raw)
        elif self.type == "naver_store_integrated_products":
            products_parsed = self.json_load(f"{DATA_PATH}/naver_store_products_parsed.json")
            product_ids = [p["productId"] for p in products_parsed if p.get("lowMallList")]
            data_raw = []
            data_parsed = []
            for id in product_ids[:10]:
                soup = self.request_bs4(id=id)
                raw = parser.get_integrated_products(soup)
                parsed = parser.parse_integrated_products_raw(raw)
                data_raw.append(raw)
                data_parsed.append(parsed)
        elif self.type == "naver_store_integrated_reviews":
            # INTEGRATED_REVIEWS
            # 20230521 currently response unauthorized
            products_parsed = self.json_load(f"{DATA_PATH}/naver_store_products_parsed.json")
            product_ids = [p["productId"] for p in products_parsed if p.get("lowMallList")]
            data_raw = []
            data_parsed = []
            for id in product_ids[:10]:
                soup = self.request_bs4(nvMid=id, page_param_name="page")
                raw = parser.get_integrated_reviews(soup)
                parsed = parser.parse_integrated_reviews_raw(raw)
                data_raw.append(raw)
                data_parsed.append(parsed)
            pass

        if data_raw:
            self.json_save(f"{DATA_PATH}/{self.type}_raw.json", data_raw)
        if data_parsed:
            self.json_save(f"{DATA_PATH}/{self.type}_parsed.json", data_parsed)

    def iter_pages(self, request_func, func, max_page=5, page_param_name="pagingIndex"):
        """
        Iterates over multiple pages of data using the provided request function and processing function.

        Args:
            request_func (function): The function to make the request for each page of data.
            func (function): The function to process the response and extract the desired data.
            max_page (int, optional): The maximum number of pages to iterate over. Defaults to 5.
            page_param_name (str, optional): The name of the parameter used for pagination. Defaults to "pagingIndex".

        Returns:
            list: A list containing the combined results from all the pages.
        """
        page_count = 1
        ret_list = []
        while True:
            resp = request_func(**{page_param_name : page_count})
            ret = func(resp)
            if page_count > max_page or ret == None:
                break
            else:
                    ret_list.extend(ret)
                    page_count += 1
        return ret_list

    def set_params(self, **kwargs):
        '''
        데이터 소스에서 필요한 parameter 정리
        기본적으로 제공해야 하는 cookie, 이외에도 args로 입력받은 내용을 정리
        '''
        self.params.update(kwargs)
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

    def request_post(self, **kwargs):
        self.set_params(**kwargs)
        try:
            resp = requests.post(self.url, headers=self.post_headers, data=json.dumps(self.params))
            resp.raise_for_status()
            resp = resp.json()
            print(f"[crawler log] executing {self.url}...")
            return resp
        except Exception as e:
            self.is_error = True
            print(f"[crawler error log] {e}")


    def request_bs4(self, id=None, **kwargs):
        self.set_params(**kwargs)
        try:
            urls = self.url + id if id else self.url_encoder(self.url, self.params)
            resp = requests.get(urls, headers=self.base_headers)
            soup = BeautifulSoup(resp.content, 'html.parser')
            resp.raise_for_status()
            print(f"[crawler log] executing {urls}...")
            return soup
        except Exception as e:
            self.is_error = True
            print(f"[crawler error log] {e}")
