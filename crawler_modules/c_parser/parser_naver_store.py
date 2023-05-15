import requests
from bs4 import BeautifulSoup
import pandas as pd
import json, math


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

    def get_product_list(self, keyword, n=50):
        '''
        TODO:
            api로 고쳐서 호출하기 (page 개수에 맞춰서)
            https://search.shopping.naver.com/api/search/all?eq=&iq=&origQuery=%EB%82%A8%EC%84%B1%20%EC%8A%A4%EB%8B%88%EC%BB%A4%EC%A6%88&pagingIndex=2&pagingSize=40&productSet=total&query=%EB%82%A8%EC%84%B1%20%EC%8A%A4%EB%8B%88%EC%BB%A4%EC%A6%88&sort=rel&viewType=list&xq=
        '''
        cat_id = ""
        frm = "" # "NVSHATC"
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

    def get_store_review(self, merchantNo="500245685", originProductNo=4662556695):
        '''
        TODO:
            merchantNo, originProductNo 가져오기 (product_list_by_request)
                merchantNo: from product_list
                originProductNo: 상품 리스트에서 찾을 수 없음
        '''
        url = 'https://m.shopping.naver.com/v1/reviews/paged-reviews'
        headers = {
            "accept": 'application/json, text/plain, */*',
            "accept-encoding": 'gzip, deflate, br',
            "accept-language": 'ko-KR,ko;q=0.9,zh-CN;q=0.8,zh;q=0.7,en-US;q=0.6,en;q=0.5',
            "content-type": 'application/json;charset=UTF-8',
            "user-agent": 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.0.0 Safari/537.36',
        }
        store_reviews = []
        page_count = 1
        while True:
            request_data = {
                "page": page_count,
                "pageSize": 20,
                "merchantNo": merchantNo,
                "originProductNo": originProductNo,
                "sortType": "REVIEW_RANKING"
            }
            response = requests.post(url, headers=headers, data=json.dumps(request_data))
            
            response = response.json()
            total_elements, total_pages, product_review = self.extract_store_review_data(response)
            store_reviews.extend(product_review)
            page_count += 1
            if page_count > total_pages:
                break
            
        return {
            "total_elements": total_elements,
            "store_reviews": store_reviews
        }


    def get_integrated_product(self, product_id):
        url = f'https://search.shopping.naver.com/catalog/{product_id}'
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

        lowestPrice, productCount, reviewCount, reviewScore, starScores = self.extract_integrated_product_data(scripts_data)

        return {
            "product_id": product_id,
            "lowestPrice": lowestPrice, 
            "productCount": productCount, 
            "reviewCount": reviewCount, 
            "reviewScore": reviewScore, 
            "starScores": starScores
        }

    def get_integrated_review(self, product_id, page_size=20):
        headers = {
            "accept": 'application/json, text/plain, */*',
            "accept-encoding": 'gzip, deflate, br',
            "accept-language": 'ko-KR,ko;q=0.9,zh-CN;q=0.8,zh;q=0.7,en-US;q=0.6,en;q=0.5',
            "content-type": 'application/json;charset=UTF-8',
            "user-agent": 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.0.0 Safari/537.36',
        }

        integrated_reviews = []
        page_count = 1
        while True:
            url = f"https://search.shopping.naver.com/api/review?isNeedAggregation=N&nvMid={product_id}&page={page_count}&pageSize={page_size}&sortType=QUALITY"
            response = requests.get(url, headers=headers)
            total_elements, integrated_review = self.extract_integrated_review_data(response)
            total_pages = math.trunc(total_elements / page_size)
            integrated_reviews.extend(integrated_review)
            page_count += 1
            if page_count > total_pages:
                break
        
        return {
            "total_elements": total_elements,
            "integrated_review": integrated_review
        }

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

    def extract_product_data(self, response):
        product_list = []
        products = response["props"]["pageProps"]["initialState"]["products"]["list"]
        for p in products:
            p = p["item"]
            product_info = {
                "productId": p.get("id"),
                "productTitle" : p.get("productTitle"), # 상품명
                "adProductInfoEnabled" : p.get("adProductInfoEnabled"), # 광고여부
                "price" : p.get("price"), # 가격
                "deliveryFeeContent" : p.get("deliveryFeeContent"), # 배송비
                "category" : [p.get("category1Name"), p.get("category2Name"), p.get("category3Name")],
                "adAdditionalDescription" : p.get("adAdditionalDescription"), # 사용자문구
                "reviewCount" : p.get("reviewCount"), # 리뷰수
                "openDate" : '-'.join([p["openDate"][:4], p["openDate"][4:6], p["openDate"][6:8]]) if p.get("openDate") else None, # 등록일
                "mallGrade" : p["mallInfoCache"].get("mallGrade") if p.get("mallInfoCache") else None, # 몰 등급
                "naverPayAdAccumulatedDisplayValue" : p.get("naverPayAdAccumulatedDisplayValue"), # 포인트 원
                "adcrUrl" : p.get("adcrUrl"), # url
                "mallNameOrg" : p.get("mallNameOrg"), # 몰 회사명
                "isSmartStore" : True if p.get("mallProductUrl") and "smartstore" in p.get("mallProductUrl") else False, # 스마트스토어 여부 0: 기타, 1: 스마트스토어, 3: 스토어 모음
                "mall" : {
                    "mallNo": p.get("mallNo"),
                    "mallId": p.get("mallId"),
                    "mallName": p.get("mallName"),
                }, # 셀러이름
                "merchantNo": p.get("chnlSeq"), # merchantNo
                "lowMallList": p.get("lowMallList") # lowMallList 최저가 사이트로 연결
                # TODO: 찜하기 -> 특이
            }
            product_list.append(product_info)
        return product_list

    def extract_store_review_data(self, response):
        
        review_list = []
        totalElements = response["totalElements"]
        totalPages = response["totalPages"]
        
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
        return totalElements, totalPages, review_list

    def extract_integrated_review_data(self, response):
        review_list = []
        totalCount = response["totalCount"]
        reviews = response["reviews"]
        
        for r in reviews:
            r = {
                "id": r.get("id"),
                "content": r.get("content"),
                "mallName": r.get("mallName"),
                "registerDate": r.get("registerDate"),
                "modifyDate": r.get("modifyDate"),
                "starScore": r.get("starScore"),
                "title": r.get("title"),
                "userId": r.get("userId"),
            }
            review_list.append(r)
        return totalCount, reviews




    def extract_integrated_product_data(self, response):
        review_response = response["props"]["pageProps"]["initialState"]["catalog"]
        integrated_response = review_response["info"]
        lowestPrice = integrated_response["lowestPrice"]
        productCount = integrated_response["productCount"]
        reviewCount = integrated_response["reviewCount"]
        reviewScore = integrated_response["reviewScore"]

        review_info = review_response["review"]["summary"]
        # averageStarScore = review_info["averageStarScore"]
        starScores = review_info["starScores"]
        
        return lowestPrice, productCount, reviewCount, reviewScore, starScores