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

    def get_product_list(self, keyword, n=50):
        # url = "/api/search/all?eq=&iq=&pagingIndex=1&pagingSize=40&productSet=total&query=%EB%82%A8%EC%84%B1%20%EC%8A%A4%EB%8B%88%EC%BB%A4%EC%A6%88&sort=price_asc&viewType=list&xq="
        
        url = f'https://search.shopping.naver.com/search/all?query={keyword}'
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36'}
        response = requests.get(url, headers=headers)
        soup = BeautifulSoup(response.content, 'html.parser')
        data_list = []
        for i in range(1, n+1):
            data = {
                "name": self.extract_product_data(soup, i, "name"),
                "is_ad": self.extract_product_data(soup, i, "is_ad"),
                "price": self.extract_product_data(soup, i, "price"),
                "shipping_fee": self.extract_product_data(soup, i, "shipping_fee"),
                "category": self.extract_product_data(soup, i, "category"),
                "ad_event_comment": self.extract_product_data(soup, i, "ad_event_comment"),
                "reviews": self.extract_product_data(soup, i, "reviews"),
                "register_date": self.extract_product_data(soup, i, "register_date"),
                "zzims": self.extract_product_data(soup, i, "zzims"),
                "seller_name": self.extract_product_data(soup, i, "seller_name"),
                "grade": self.extract_product_data(soup, i, "grade"),
                "reward_naver_points": self.extract_product_data(soup, i, "reward_naver_points"),
                "url": self.extract_product_data(soup, i, "url"),
                "is_smartstore": self.extract_product_data(soup, i, "is_smartstore"),
            }
            if data["name"] == None and data["price"] == None:
                break
            data_list.append(data)

        return data_list

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

    def extract_product_data(self, soup, i, name):
        '''
        html 태그에서 가져오는 방식으로는 상위 5개밖에 가져오지 못함
        TODO: modify to get top n results
        '''
        selector_dict = {
            "name": f"#content > div.style_content__xWg5l > div.basicList_list_basis__uNBZx > div > div:nth-child({i}) > div > div > div.basicList_info_area__TWvzp > div.basicList_title__VfX3c > a",
            "is_ad": f"#content > div.style_content__xWg5l > div.basicList_list_basis__uNBZx > div > div:nth-child({i}) > div > div > div.basicList_info_area__TWvzp > div.basicList_price_area__K7DDT > button",
            "price": f"#content > div.style_content__xWg5l > div.basicList_list_basis__uNBZx > div > div:nth-child({i}) > div > div > div.basicList_info_area__TWvzp > div.basicList_price_area__K7DDT > strong > span > span.price_price__LEGN7 > span",
            "shipping_fee": f"#content > div.style_content__xWg5l > div.basicList_list_basis__uNBZx > div > div:nth-child({i}) > div > div > div.basicList_info_area__TWvzp > div.basicList_price_area__K7DDT > strong > span > span.price_delivery__yw_We",
            "category": f"#content > div.style_content__xWg5l > div.basicList_list_basis__uNBZx > div > div:nth-child({i}) > div > div > div.basicList_info_area__TWvzp > div.basicList_depth__SbZWF > span",
            "ad_event_comment": f"#content > div.style_content__xWg5l > div.basicList_list_basis__uNBZx > div > div:nth-child({i}) > div > div > div.basicList_info_area__TWvzp > div.basicList_desc__3kwkT > div > a",
            "reviews": f"#content > div.style_content__xWg5l > div.basicList_list_basis__uNBZx > div > div:nth-child({i}) > div > div > div.basicList_info_area__TWvzp > div.basicList_etc_box__5lkgg > a > em",
            "register_date": f"#content > div.style_content__xWg5l > div.basicList_list_basis__uNBZx > div > div:nth-child({i}) > div > div > div.basicList_info_area__TWvzp > div.basicList_etc_box__5lkgg > span:nth-child(2)",
            "zzims": f"#content > div.style_content__xWg5l > div.basicList_list_basis__uNBZx > div > div:nth-child({i}) > div > div > div.basicList_info_area__TWvzp > div.basicList_etc_box__5lkgg > span:nth-child(3) > a > span > em",
            "seller_name": f"#content > div.style_content__xWg5l > div.basicList_list_basis__uNBZx > div > div:nth-child({i}) > div > div > div.basicList_mall_area__faH62 > div.basicList_mall_title__FDXX5 > a.basicList_mall__BC5Xu.linkAnchor",
            "grade": f"#content > div.style_content__xWg5l > div.basicList_list_basis__uNBZx > div > div:nth-child({i}) > div > div > div.basicList_mall_area__faH62 > div.basicList_mall_grade__1hPzs > span",
            "reward_naver_points": f"#content > div.style_content__xWg5l > div.basicList_list_basis__uNBZx > div > div:nth-child({i}) > div > div > div.basicList_mall_area__faH62 > ul > li:nth-child(1) > span.n_npay_info__TqvjM > span",
            "url": f"#content > div.style_content__xWg5l > div.basicList_list_basis__uNBZx > div > div:nth-child({i}) > div > div > div.basicList_info_area__TWvzp > div.basicList_title__VfX3c > a",
            "is_smartstore": f""
        }
        selector = selector_dict.get(name)
        if not selector:
            return
        result = soup.select(selector)
        if name[:3] == "is_":
            return True if result else False
        if not result:
            return None

        if name == "url":
            return result[0].attrs.get("href")
        elif name == "register_date":
            return result[0].text.replace('등록일 ', '')
        elif name == "reward_naver_points":
            return result[0].text.replace('포인트 ', '')

        if len(result) > 1:
            return [r.text for r in result]
        else:
            return result[0].text

