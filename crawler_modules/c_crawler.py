import sys
import math
import os
import requests
from time import sleep
from random import randint
from crawler_modules.c_modules import Commons, get_envs
from crawler_modules.c_parser import (
    parser_dummy_site,
    parser_naver_store,
    parser_instagram,
    parser_tictoc,
)
from crawler_modules.c_parser.parser_naver_store import NaverShoppingCrawler
from bs4 import BeautifulSoup
import json

from instagrapi import Client


class Crawler(Commons):
    base_headers = {
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.110 Safari/537.36",
        # "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
        # "accept-language": "en-US;en;q=0.9",
        # "accept-encoding": "gzip, deflate, br",
    }
    post_headers = {
        "accept": "application/json, text/plain, */*",
        "accept-encoding": "gzip, deflate, br",
        "accept-language": "ko-KR,ko;q=0.9,zh-CN;q=0.8,zh;q=0.7,en-US;q=0.6,en;q=0.5",
        "content-type": "application/json;charset=UTF-8",
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.0.0 Safari/537.36",
    }

    def __init__(self, type: str, query=None, items=None, **kwargs) -> None:
        """
        query 및 items의 경우 특정 키워드 검색 등을 위해 일단 구성
        차후 개발 명세에 따로 수정 가능
        """
        super().__init__()
        _envs = get_envs()
        self.page = 1
        self.type = type
        self.items = items
        self.query = query
        self.is_error = False
        self.url = _envs[type]["url"]
        self.params = _envs[type].get("params", {})
        self.parser = eval(_envs[type]["parser"])

        # For instagram, open source 사용 (https://github.com/adw0rd/instagrapi)
        self.insta_cl = None
        if type == "instagram":
            self.insta_cl = Client()
            self.insta_cl.login(kwargs["insta_id"], kwargs["insta_pw"])

    def execute(self, **kwargs):
        """
        개별 parser에서 데이터 처리
        execute는 1 request로 한정 (다만 마우스 스크롤, next page가 있는 경우에는 별도 조치 필요)
        여러 개의 키워드 쿼리가 있는 경우 main.py에서 iterate 수행
        """
        # For Naver Store
        # _raw : response의 모든 내용
        # _parsed : 파싱 후 정리된 내용
        # output : /data에 json파일 저장
        # - 1. naver_store_keyword_info 입력 키워드 관련 정보
        # - 2. naver_store_products 입력 키워드의 모든 상품 정보
        # - 3. naver_store_product_reviews 특정 스마트 스토어의 리뷰 정보
        # - 4. naver_store_integrated_products 통합 상품 정보 (11번가, 쿠팡 등 최저가 페이지)
        DATA_PATH = os.path.dirname(os.path.realpath(__file__)) + "/data"
        data_raw = None
        data_parsed = None

        if "naver_store_" in self.type:
            parser = self.parser()
            if self.type == "naver_store_keyword_info":
                soup = self.request_bs4()
                data_parsed = parser.get_keyword_info(soup)
            elif self.type == "naver_store_products":
                data_raw = self.iter_pages(
                    self.request_bs4, parser.get_products, page_param_name="pagingIndex"
                )
                data_parsed = parser.parse_products_raw(data_raw)
            elif self.type == "naver_store_product_reviews":
                data_raw = self.iter_pages(
                    self.request_post,
                    parser.get_store_product_reviews,
                    page_param_name="page",
                )
                data_parsed = parser.parse_store_product_reviews_raw(data_raw)
            elif self.type == "naver_store_integrated_products":
                products_parsed = self.json_load(
                    f"{DATA_PATH}/naver_store_products_parsed.json"
                )
                product_ids = [
                    p["productId"] for p in products_parsed if p.get("lowMallList")
                ]
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
                products_parsed = self.json_load(
                    f"{DATA_PATH}/naver_store_products_parsed.json"
                )
                product_ids = [
                    p["productId"] for p in products_parsed if p.get("lowMallList")
                ]
                data_raw = []
                data_parsed = []
                for id in product_ids[:10]:
                    soup = self.request_bs4(nvMid=id, page_param_name="page")
                    raw = parser.get_integrated_reviews(soup)
                    parsed = parser.parse_integrated_reviews_raw(raw)
                    data_raw.append(raw)
                    data_parsed.append(parsed)

            if data_raw:
                self.json_save(f"{DATA_PATH}/{self.type}_raw.json", data_raw)
            if data_parsed:
                self.json_save(f"{DATA_PATH}/{self.type}_parsed.json", data_parsed)
            return True

        # For instagram, open source 사용 (https://github.com/adw0rd/instagrapi)
        # - 요구 데이터 추가 시 관련 메서드 찾아서 추가 필요
        # - 현재 구현되어 있는 메서드 4종
        # - 1. 해시태그 인포 >> 해시태그 팔로워 수등
        # - 2. 해시태그 인기 게시물 >> 해시태그 인기 게시물 리스트
        # - 3. 해시태그 관련 게시물 >> 해시태그 관련 게시물 리스트
        # - 4. 유저 게시물 >> 유저의 게시물 리스트
        elif self.type == "instagram":
            if "hashtag_info" in kwargs:
                data = self.insta_cl.hashtag_info(kwargs["hashtag_info"])
            elif "hashtag_media_top" in kwargs:
                data = self.insta_cl.hashtag_medias_top(kwargs["hashtag_media_top"])
            elif "hashtag_media_rct" in kwargs:
                data = self.insta_cl.hashtag_medias_recent(kwargs["hashtag_media_rct"])
            elif "user_media" in kwargs:
                user = self.insta_cl.user_id_from_username(kwargs["user_media"])
                data = self.insta_cl.user_medias(user, 20)

        # For tictoc
        # - 대부분 간단한 xpath selector 해결가능
        # - 1. 해시태그 인포
        # - 2. 해시태그 리스트 및 정보
        # - 3. 음원 관련 리스트
        # - 4. 유저 인포
        elif self.type == "tictoc":
            if "hashtag_info" in kwargs:
                self.url = f"https://www.tiktok.com/tag/{kwargs['hashtag_info']}"
            elif "hashtag_list" in kwargs:
                self.url = f"https://www.tiktok.com/tag/{kwargs['hashtag_list']}"
            elif "music_list" in kwargs:
                self.url = f"https://www.tiktok.com/music/{kwargs['music_list']}"
            elif "user_info" in kwargs:
                self.url = f"https://www.tiktok.com/@{kwargs['user_info']}"
            resp = self.request_html()
            pser = self.parser.parser_tictoc()
            data = pser.datas(resp.text, list(kwargs.keys())[0])
            return data
        else:
            raise KeyError("Choose the correct type of crawler.")
        return data

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
            resp = request_func(**{page_param_name: page_count})
            ret = func(resp)
            if page_count > max_page or ret == None:
                break
            else:
                ret_list.extend(ret)
                page_count += 1
        return ret_list

    def set_params(self, **kwargs):
        """
        데이터 소스에서 필요한 parameter 정리
        기본적으로 제공해야 하는 cookie, 이외에도 args로 입력받은 내용을 정리
        """
        if kwargs != {}:
            self.params.update(kwargs)

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
            resp = requests.post(
                self.url, headers=self.post_headers, data=json.dumps(self.params)
            )
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
            soup = BeautifulSoup(resp.content, "html.parser")
            resp.raise_for_status()
            print(f"[crawler log] executing {urls}...")
            return soup
        except Exception as e:
            self.is_error = True
            print(f"[crawler error log] {e}")
