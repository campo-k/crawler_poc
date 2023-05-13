import math
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
        # resp = self.request_html()
        # data = self.parser(resp.text)
        parser = self.parser()
        keyword_info = parser.get_keyword_info(keyword)
        product_list = parser.get_product_list(keyword)
        print(keyword_info)
        print(product_list)
    
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
