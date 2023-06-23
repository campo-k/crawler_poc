import json
from urllib import parse
from datetime import datetime

crawler_variables = {
    "dummy_site": {
        "url": "https://www.dummysite.com/search?",
        "params": [],
        "parser": "parser_dummy"
    },
    "naver_store": {
        "url": "",
        "params": {},
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
