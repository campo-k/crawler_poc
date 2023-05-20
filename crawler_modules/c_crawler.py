import sys
import math
import requests
from time import sleep
from random import randint
from crawler_modules.c_modules import Commons, get_envs
from crawler_modules.c_parser import parser_dummy_site

from instagrapi import Client


class Crawler(Commons):
    base_headers = {
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.110 Safari/537.36",
        "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
        "accept-language": "en-US;en;q=0.9",
        "accept-encoding": "gzip, deflate, br",
    }

    def __init__(self, type: str, query=None, items=None, **kwargs) -> None:
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
        # To-jungsub 
        # - 아래 부분은 parser를 하나밖에 쓸수 없는 구조입니다.
        # - get_envs()통해 반환되는 parser string을 활용하기 위해서는 다른 방법이 필요합니다.
        # self.parser = getattr(parser_dummy_site, _envs[type]["parser"])
        
        # For instagram, open source 사용 (https://github.com/adw0rd/instagrapi)
        self.insta_cl = None 
        if type == 'instagram':
            self.insta_cl = Client()
            self.insta_cl.login(kwargs['insta_id'], kwargs['insta_pw'])

    def execute(self, **kwargs):
        '''
        개별 parser에서 데이터 처리
        execute는 1 request로 한정 (다만 마우스 스크롤, next page가 있는 경우에는 별도 조치 필요)
        여러 개의 키워드 쿼리가 있는 경우 main.py에서 iterate 수행 
        '''
        data = None

        # For instagram, open source 사용 (https://github.com/adw0rd/instagrapi)
        # - 요구 데이터 추가 시 관련 메서드 찾아서 추가 필요
        # - 현재 구현되어 있는 메서드 4종
        # - 1. 해시태그 인포 >> 해시태그 팔로워 수등
        # - 2. 해시태그 인기 게시물 >> 해시태그 인기 게시물 리스트
        # - 3. 해시태그 관련 게시물 >> 해시태그 관련 게시물 리스트
        # - 4. 유저 게시물 >> 유저의 게시물 리스트
        if self.type == 'instagram':
            if   "hashtag_info" in kwargs:
                data = self.insta_cl.hashtag_info(kwargs["hashtag_info"])
            elif "hashtag_media_top" in kwargs:
                data = self.insta_cl.hashtag_medias_top(kwargs["hashtag_media_top"])
            elif "hashtag_media_rct" in kwargs:
                data = self.insta_cl.hashtag_medias_recent(kwargs["hashtag_media_rct"])
            elif "user_media" in kwargs:
                user = self.insta_cl.user_id_from_username(kwargs["user_media"])
                data = self.insta_cl.user_medias(user, 20)
        else:
            resp = self.request_html()
            data = self.parser(resp.text)
        return data        
    
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
