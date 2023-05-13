import requests
from bs4 import BeautifulSoup
import pandas as pd

class NaverShoppingCrawler:
    def __init__(self):
        pass

    def get_keyword_info(self, keyword):
        url = f'https://search.shopping.naver.com/search/all?query={keyword}'
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36'}
        response = requests.get(url, headers=headers)
        soup = BeautifulSoup(response.content, 'html.parser')
        relation_tags = self.extract_keyword_data(soup, "relation_tag")
        categories = self.extract_keyword_data(soup, "category")
        brands = self.extract_keyword_data(soup, "brand")
        prices = self.extract_keyword_data(soup, "price")
        subfilter_nums = self.extract_keyword_data(soup, "subfilter_num")
        data = {
            'relation_tags': relation_tags,
            'category': categories,
            'brand': brands,
            'price': prices,
            'subfilter_nums': subfilter_nums,
        }
        return data
        # df = pd.DataFrame(data)
        # df.to_csv('naver_shopping_data.csv', index=False)


    def extract_keyword_data(self, soup, name):
        data_list = []
        selector_dict = {
            "relation_tag": "#container > div.relatedTags_relation_tag__Ct0q2 > div.relatedTags_relation_srh__YG9s7 > ul > li",
            "category": "#container > div.style_inner__i4gKy > div.filter_finder__E_I19 > div > div:nth-child(2) > div.filter_finder_row__ILuuO > div > ul > li",
            "brand": "#container > div.style_inner__i4gKy > div.filter_finder__E_I19 > div > div.filter_finder_col__k6BKF.filter_is_fixed__xmAmM > div.filter_finder_row__ILuuO > ul > li",
            "price": "#container > div.style_inner__i4gKy > div.filter_finder__E_I19 > div > div.filter_finder_col__k6BKF.filter_finder_price__dQExh > div.finder_price_inner > ul > li > a",
            "subfilter_num": "#content > div.style_content__xWg5l > div.seller_filter_area > ul > li > a > span.subFilter_num__S9sle"
        }
        selector = selector_dict.get(name, "")
        tags = soup.select(selector)
        for tag in tags:
            data = tag.text.strip().replace('HIT', '')
            data_list.append(data)
        return data_list
