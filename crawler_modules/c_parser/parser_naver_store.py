import requests
from bs4 import BeautifulSoup
import pandas as pd
import json

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

    # def get_product_list(self, keyword, n=50):
    #     # url = "/api/search/all?eq=&iq=&pagingIndex=1&pagingSize=40&productSet=total&query=%EB%82%A8%EC%84%B1%20%EC%8A%A4%EB%8B%88%EC%BB%A4%EC%A6%88&sort=price_asc&viewType=list&xq="

    #     url = f'https://search.shopping.naver.com/search/all?query={keyword}'
    #     headers = {
    #         'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36'}
    #     response = requests.get(url, headers=headers)
    #     soup = BeautifulSoup(response.content, 'html.parser')
    #     data_list = []
    #     for i in range(1, n+1):
    #         data = {
    #             "name": self.extract_product_data(soup, i, "name"),
    #             "is_ad": self.extract_product_data(soup, i, "is_ad"),
    #             "price": self.extract_product_data(soup, i, "price"),
    #             "shipping_fee": self.extract_product_data(soup, i, "shipping_fee"),
    #             "category": self.extract_product_data(soup, i, "category"),
    #             "ad_event_comment": self.extract_product_data(soup, i, "ad_event_comment"),
    #             "reviews": self.extract_product_data(soup, i, "reviews"),
    #             "register_date": self.extract_product_data(soup, i, "register_date"),
    #             "zzims": self.extract_product_data(soup, i, "zzims"),
    #             "seller_name": self.extract_product_data(soup, i, "seller_name"),
    #             "grade": self.extract_product_data(soup, i, "grade"),
    #             "reward_naver_points": self.extract_product_data(soup, i, "reward_naver_points"),
    #             "url": self.extract_product_data(soup, i, "url"),
    #             "is_smartstore": self.extract_product_data(soup, i, "is_smartstore"),
    #         }
    #         if data["name"] == None and data["price"] == None:
    #             break
    #         data_list.append(data)

    #     return data_list

    def get_product_list(self, keyword, n=50):
        cat_id = ""
        frm = "NVSHATC"
        url = f'https://search.shopping.naver.com/search/all?query={keyword}&cat_id={cat_id}&frm={frm}'
        headers = {
            "accept": 'application/json, text/plain, */*',
            "accept-encoding": 'gzip, deflate, br',
            "accept-language": 'ko-KR,ko;q=0.9,zh-CN;q=0.8,zh;q=0.7,en-US;q=0.6,en;q=0.5',
            "content-type": 'application/json;charset=UTF-8',
            "user-agent": 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.0.0 Safari/537.36',
        }
        response = requests.get(url, headers=headers)
        soup = BeautifulSoup(response.content, 'html.parser')
        scripts = soup.find("script", {"id": "__NEXT_DATA__"})
        scripts_data = json.loads(scripts.text.replace(';','').strip())
        products = self.extract_product_data(scripts_data)
        return products

    def get_store_review(self, request_ids):
        '''
        TODO:
            merchant_id, product_id 가져오기 (product_list_by_request)
            review 개수가 많은 상품
        '''
        url = 'https://m.shopping.naver.com/v1/reviews/paged-reviews'
        headers = {
            "accept": 'application/json, text/plain, */*',
            "accept-encoding": 'gzip, deflate, br',
            "accept-language": 'ko-KR,ko;q=0.9,zh-CN;q=0.8,zh;q=0.7,en-US;q=0.6,en;q=0.5',
            "content-type": 'application/json;charset=UTF-8',
            "user-agent": 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.0.0 Safari/537.36',
        }
        data_list = []
        for merchant_id,product_id in request_ids:
            request_data = {
                "page": 1,
                "pageSize": 20,
                # "merchantNo": "500154868",
                "merchantNo": merchant_id,
                # "originProductNo": "4451093970",
                "originProductNo": product_id,
                "sortType": "REVIEW_RANKING"
            }
            response = requests.post(url, headers=headers, data=json.dumps(request_data))
            response = response.json()
            product_review = self.extract_store_review_data(self, response)
            data_list.append(product_review)
            
        return data_list

    def get_integrated_review():
        pass

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

    # def extract_product_data(self, soup, i, name):
    #     '''
    #     html 태그에서 가져오는 방식으로는 상위 5개밖에 가져오지 못함
    #     TODO: 
    #         try request api to get all results
    #     '''
    #     selector_dict = {
    #         "name": f"#content > div.style_content__xWg5l > div.basicList_list_basis__uNBZx > div > div:nth-child({i}) > div > div > div.basicList_info_area__TWvzp > div.basicList_title__VfX3c > a",
    #         "is_ad": f"#content > div.style_content__xWg5l > div.basicList_list_basis__uNBZx > div > div:nth-child({i}) > div > div > div.basicList_info_area__TWvzp > div.basicList_price_area__K7DDT > button",
    #         "price": f"#content > div.style_content__xWg5l > div.basicList_list_basis__uNBZx > div > div:nth-child({i}) > div > div > div.basicList_info_area__TWvzp > div.basicList_price_area__K7DDT > strong > span > span.price_price__LEGN7 > span",
    #         "shipping_fee": f"#content > div.style_content__xWg5l > div.basicList_list_basis__uNBZx > div > div:nth-child({i}) > div > div > div.basicList_info_area__TWvzp > div.basicList_price_area__K7DDT > strong > span > span.price_delivery__yw_We",
    #         "category": f"#content > div.style_content__xWg5l > div.basicList_list_basis__uNBZx > div > div:nth-child({i}) > div > div > div.basicList_info_area__TWvzp > div.basicList_depth__SbZWF > span",
    #         "ad_event_comment": f"#content > div.style_content__xWg5l > div.basicList_list_basis__uNBZx > div > div:nth-child({i}) > div > div > div.basicList_info_area__TWvzp > div.basicList_desc__3kwkT > div > a",
    #         "reviews": f"#content > div.style_content__xWg5l > div.basicList_list_basis__uNBZx > div > div:nth-child({i}) > div > div > div.basicList_info_area__TWvzp > div.basicList_etc_box__5lkgg > a > em",
    #         "register_date": f"#content > div.style_content__xWg5l > div.basicList_list_basis__uNBZx > div > div:nth-child({i}) > div > div > div.basicList_info_area__TWvzp > div.basicList_etc_box__5lkgg > span:nth-child(2)",
    #         "zzims": f"#content > div.style_content__xWg5l > div.basicList_list_basis__uNBZx > div > div:nth-child({i}) > div > div > div.basicList_info_area__TWvzp > div.basicList_etc_box__5lkgg > span:nth-child(3) > a > span > em",
    #         "seller_name": f"#content > div.style_content__xWg5l > div.basicList_list_basis__uNBZx > div > div:nth-child({i}) > div > div > div.basicList_mall_area__faH62 > div.basicList_mall_title__FDXX5 > a.basicList_mall__BC5Xu.linkAnchor",
    #         "grade": f"#content > div.style_content__xWg5l > div.basicList_list_basis__uNBZx > div > div:nth-child({i}) > div > div > div.basicList_mall_area__faH62 > div.basicList_mall_grade__1hPzs > span",
    #         "reward_naver_points": f"#content > div.style_content__xWg5l > div.basicList_list_basis__uNBZx > div > div:nth-child({i}) > div > div > div.basicList_mall_area__faH62 > ul > li:nth-child(1) > span.n_npay_info__TqvjM > span",
    #         "url": f"#content > div.style_content__xWg5l > div.basicList_list_basis__uNBZx > div > div:nth-child({i}) > div > div > div.basicList_info_area__TWvzp > div.basicList_title__VfX3c > a",
    #         "is_smartstore": f""
    #     }
    #     selector = selector_dict.get(name)
    #     if not selector:
    #         return
    #     result = soup.select(selector)
    #     if name[:3] == "is_":
    #         return True if result else False
    #     if not result:
    #         return None

    #     if name == "url":
    #         return result[0].attrs.get("href")
    #     elif name == "register_date":
    #         return result[0].text.replace('등록일 ', '')
    #     elif name == "reward_naver_points":
    #         return result[0].text.replace('포인트 ', '')

    #     if len(result) > 1:
    #         return [r.text for r in result]
    #     else:
    #         return result[0].text

    def extract_product_data(self, response):
        product_list = []
        products = response["props"]["pageProps"]["initialState"]["products"]["list"]
        for p in products:
            product_info = {
                "productTitle" : p.get("productTitle"), # 상품명
                "adProductInfoEnabled" : p.get("adProductInfoEnabled"), # 광고여부
                "price" : p.get("price"), # 가격
                "deliveryFeeContent" : p.get("deliveryFeeContent"), # 배송비
                "category" : [p.get("category1Name"), p.get("category2Name"), p.get("category3Name")],
                "adAdditionalDescription" : p.get("adAdditionalDescription"), # 사용자문구
                "reviewCount" : p.get("reviewCount"), # 리뷰수
                "openDate" : p.get("openDate"), # 등록일
                "mallGrade" : p["mallInfoCache"].get("mallGrade") if p.get("mallInfoCache") else None, # 몰 등급
                "naverPayAdAccumulatedDisplayValue" : p.get("naverPayAdAccumulatedDisplayValue"), # 포인트 원
                "adcrUrl" : p.get("adcrUrl"), # url
                "mallNameOrg" : p.get("mallNameOrg"), # 몰 회사명
                "isBrandStore" : p.get("isBrandStore"), # 스마트스토어 여부 0: 기타, 1: 스마트스토어, 3: 스토어 모음
                "mall" : {
                    "mallNo": p.get("mallNo"),
                    "mallId": p.get("mallId"),
                    "mallName": p.get("mallName"),
                } # 셀러이름
                # TODO: 찜하기 -> 특이
            }
            product_list.append(product_info)
        return product_list

    def extract_store_review_data(self, response):
        
        review_list = []
        totalElements = response["totalElements"]
        
        response_reviews = response["contents"]
        for review in response_reviews:
            '''
            날짜 (yyyy-mm-dd 포맷으로 통일)
            아이디(혹시 마킹된 것 아이디 알아낼 수 있는 방법이 있는지 한 번 봐주시면 땡큐 배리 감사!)
            후기 TEXT만 (신발이 디자인이~~ 리네요~)
            별점 점수
            '''
            r = {
                "id": review.get("id"),
                "createDate": review.get("createDate").split("T")[0],
                "writerMemberId": review.get("writerMemberId"),
                "reviewContent": review.get("reviewContent"),
                "reviewScore": review.get("reviewScore"),
            }
            review_list.append(r)
        return {
            "totalElements": totalElements,
            "reviews": review_list
        }

    def extract_integrated_review_data():
        pass
