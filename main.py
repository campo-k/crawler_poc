from crawler_modules.c_crawler import *

if __name__ == "__main__":
    
    # For instagram, open source 사용 (https://github.com/adw0rd/instagrapi)
    # - 요구 데이터 추가 시 관련 메서드 찾아서 추가 필요
    # - 현재 구현되어 있는 메서드 4종
    # - 1. 해시태그 인포 >> 해시태그 팔로워 수등
    # - 2. 해시태그 인기 게시물 >> 해시태그 인기 게시물 리스트
    # - 3. 해시태그 관련 게시물 >> 해시태그 관련 게시물 리스트
    # - 4. 유저 게시물 >> 유저의 게시물 리스트

    # Instagram open source crawler initialize.
    INSTA_USER_NAME = ""
    INSTA_USER_PASS = ""
    crawler = Crawler(
        "instagram", 
        insta_id=INSTA_USER_NAME, 
        insta_pw=INSTA_USER_PASS
    )
    # hashtag 관련
    ht_info = crawler.execute(hashtag_info= "살로몬")
    ht_media_tops = crawler.execute(hashtag_media_top= "살로몬")
    ht_media_rcts = crawler.execute(hashtag_media_rct= "살로몬")\
    # user 관련
    user_media = crawler.execute(user_media= "ssunnyday__")
    # result print!!
    print(f"[Instagram ht_info result] {ht_info.name} / {ht_info.media_count}")
    print(f"[Instagram ht_media_tops result] {[h.caption_text for h in ht_media_tops]}")
    print(f"[Instagram ht_media_rcts result] {[h.caption_text for h in ht_media_rcts]}")
    print(f"[Instagram user_media result] {[h.caption_text for h in user_media]}")

    crawler = Crawler("naver_store")
    # 키워드 관련 
    # ex. 연관검색어, 카테고리, 브랜드 등
    crawler.execute(name="keyword_info", query="남성 스니커즈")
    # 상품 관련
    # ex. 광고여부, 가격, 배송비 등
    crawler.execute(name="products", query="남성 스니커즈", cat_id="", frm="", max_page=5)
    # 상품 리뷰 관련
    # ex. 리뷰 작성일, 작성자, 내용, 점수 등
    crawler.execute(name="product_reviews", query="500245685", pageSize=20, merchantNo="500245685", originProductNo=4662556695, sortType="REVIEW_RANKING")
    # 통합 상품 관련
    # ex. 최저가, 판매자 개수, 통합 리뷰 개수, 통합 리뷰 점수 등
    # lowMallList가 존재하는 products만 검색 가능
    crawler.execute(name="integrated_products", products=["31708195754","26619051114"])
