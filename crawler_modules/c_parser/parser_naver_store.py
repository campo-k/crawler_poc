import requests
from bs4 import BeautifulSoup
import pandas as pd

class NaverShoppingCrawler:
    def __init__(self):
        pass

    def crawl(self, keyword):
        url = f'https://search.shopping.naver.com/search/all?query={keyword}'
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36'}
        response = requests.get(url, headers=headers)
        soup = BeautifulSoup(response.content, 'html.parser')
        relation_tags = self.extract_relation_tags(soup)
        categories = self.extract_categories(soup)
        brands = self.extract_brands(soup)
        prices = self.extract_prices(soup)
        subfilter_nums = self.extract_subfilter_num(soup)
        data = {
            'relation_tags': relation_tags,
            'category': categories,
            'brand': brands,
            'price': prices,
            'subfilter_nums': subfilter_nums,
        }
        df = pd.DataFrame(data)
        df.to_csv('naver_shopping_data.csv', index=False)
        pass

    #TODO: sometimes there is no relation tags
    def extract_relation_tags(self, soup):
        relation_tags = []
        related_keywords = soup.select('#container > div.relatedTags_relation_tag__Ct0q2 > div.relatedTags_relation_srh__YG9s7 > ul > li')
        for related_keyword in related_keywords:
            keyword = related_keyword.text.strip()
            relation_tags.append(keyword)
        return relation_tags
        

    def extract_categories(self, soup):
        categories = []
        category_tags = soup.select('#container > div.style_inner__i4gKy > div.filter_finder__E_I19 > div > div:nth-child(2) > div.filter_finder_row__ILuuO > div > ul > li')
        for category_tag in category_tags:
            category = category_tag.text.strip().replace('HIT', '')
            categories.append(category)
        return categories

    def extract_brands(self, soup):
        brands = []
        brand_tags = soup.select('#container > div.style_inner__i4gKy > div.filter_finder__E_I19 > div > div.filter_finder_col__k6BKF.filter_is_fixed__xmAmM > div.filter_finder_row__ILuuO > ul > li')
        for brand_tag in brand_tags:
            brand = brand_tag.text.strip().replace('HIT', '')
            brands.append(brand)
        return brands

    def extract_prices(self, soup):
        prices = []
        price_tags = soup.select('#container > div.style_inner__i4gKy > div.filter_finder__E_I19 > div > div.filter_finder_col__k6BKF.filter_finder_price__dQExh > div.finder_price_inner > ul > li > a')
        for price_tag in price_tags:
            price = price_tag.text.strip().replace('HIT', '')
            prices.append(price)
        return prices

    def extract_subfilter_num(self, soup):
        subfilter_nums = []
        subfilter_tags = soup.select('#content > div.style_content__xWg5l > div.seller_filter_area > ul > li > a > span.subFilter_num__S9sle')
        for subfilter_tag in subfilter_tags:
            subfilter_num = subfilter_tag.text.strip().replace('HIT', '')
            subfilter_nums.append(subfilter_num)
        return subfilter_nums
