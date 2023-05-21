import requests
import json, math

class NaverShoppingCrawler:
    def __init__(self):
        pass

    def get_keyword_info(self, soup):
        """
        Extracts keyword information from the provided soup object.

        Args:
            soup: BeautifulSoup object representing the HTML page.

        Returns:
            A dictionary containing the extracted keyword information:
                - relation_tags: List of related tags.
                - category: List of categories.
                - brand: List of brands.
                - price: List of prices.
                - subfilter_nums: List of subfilter numbers.
        """
        relation_tags = self.extract_keyword_info_raw(soup, "relation_tag")
        categories = self.extract_keyword_info_raw(soup, "category")
        brands = self.extract_keyword_info_raw(soup, "brand")
        prices = self.extract_keyword_info_raw(soup, "price")
        subfilter_nums = self.extract_keyword_info_raw(soup, "subfilter_num")
        data = {
            'relation_tags': relation_tags,
            'category': categories,
            'brand': brands,
            'price': prices,
            'subfilter_nums': subfilter_nums,
        }
        return data

    def get_products(self, soup):
        """
        Extracts product information from the provided soup object.

        Args:
            soup: BeautifulSoup object representing the HTML page.

        Returns:
            A list of products extracted from the soup object.
        """
        scripts = soup.find("script", {"id": "__NEXT_DATA__"})
        scripts_data = json.loads(scripts.text.replace(';','').strip())
        products = self.extract_products(scripts_data)
        return products

    def get_store_product_reviews(self, resp):
        """
        Extracts store product reviews from the provided response.

        Args:
            resp: Response object containing the store product reviews.

        Returns:
            The raw data of store product reviews.
        """
        '''
            merchantNo: from product_list
            originProductNo: 상품 리스트에서 찾을 수 없음
        '''
        product_review_raw = self.extract_store_product_reviews(resp)
            
        return product_review_raw

    def get_integrated_products(self, soup):
        """
        Extracts integrated product information from the provided soup object.

        Args:
            soup: BeautifulSoup object representing the HTML page.

        Returns:
            The raw data of integrated products.
        """
        scripts = soup.find("script", {"id": "__NEXT_DATA__"})
        scripts_data = json.loads(scripts.text.replace(';','').strip())
        integrated_products_raw = self.extract_integrated_products(scripts_data)
        return integrated_products_raw

    def get_integrated_reviews(self, resp):
        """
        Retrieves integrated reviews from the provided response.

        Args:
            resp: Response object containing the store product reviews.


        Returns:
            The integrated review.
        """
        integrated_review = self.extract_integrated_reviews(resp)
        
        return integrated_review

    def extract_keyword_info_raw(self, soup, name):
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

    def extract_products(self, response):
        products = response["props"]["pageProps"]["initialState"]["products"]["list"]
        return products
    
    def extract_store_product_reviews(self, response):
        totalElements = response["totalElements"]
        totalPages = response["totalPages"]
        
        response_reviews = response["contents"]
        return response_reviews

    def extract_integrated_reviews(self, response):
        totalCount = response["totalCount"]
        reviews = response["reviews"]
        return totalCount, reviews

    def extract_integrated_products(self, response):
        review_response = response["props"]["pageProps"]["initialState"]["catalog"]
        return review_response
    
    def parse_products_raw(self, raw):
        product_list = []
        for p in raw:
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

    def parse_store_product_reviews_raw(self, raw):
        review_list = []
        for review in raw:
            r = {
                "id": review.get("id"),
                "createDate": review.get("createDate").split("T")[0],
                "writerMemberId": review.get("writerMemberId"),
                "reviewContent": review.get("reviewContent"),
                "reviewScore": review.get("reviewScore"),
            }
            review_list.append(r)
        return review_list

    def parse_integrated_reviews_raw(self, raw):
        review_list = []
        for r in raw:
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
        return review_list

    def parse_integrated_products_raw(self, raw):
        integrated_response = raw["info"]
        id = integrated_response["nvMid"]
        lowestPrice = integrated_response["lowestPrice"]
        productCount = integrated_response["productCount"]
        reviewCount = integrated_response["reviewCount"]
        reviewScore = integrated_response["reviewScore"]

        review_info = raw["review"]["summary"]
        # averageStarScore = review_info["averageStarScore"]
        starScores = review_info["starScores"]
        return {
            "id": id,
            "lowestPrice": lowestPrice, 
            "productCount": productCount, 
            "reviewCount": reviewCount, 
            "reviewScore": reviewScore, 
            "starScores": starScores
        }