from crawler_modules.c_crawler import *

if __name__ == "__main__":
    # instagram crawler
    if False:
        INSTA_USER_NAME = ""
        INSTA_USER_PASS = ""
        # Instagram open source crawler initialize.
        crawler = Crawler(
            "instagram", insta_id=INSTA_USER_NAME, insta_pw=INSTA_USER_PASS
        )
        # hashtag 관련
        ht_info = crawler.execute(hashtag_info="살로몬")
        ht_media_tops = crawler.execute(hashtag_media_top="살로몬")
        ht_media_rcts = crawler.execute(hashtag_media_rct="살로몬")
        # user 관련
        user_media = crawler.execute(user_media="ssunnyday__")
        # result print!!
        print(f"[Instagram ht_info result] {ht_info.name} / {ht_info.media_count}")
        print(
            f"[Instagram ht_media_tops result] {[h.caption_text for h in ht_media_tops]}"
        )
        print(
            f"[Instagram ht_media_rcts result] {[h.caption_text for h in ht_media_rcts]}"
        )
        print(f"[Instagram user_media result] {[h.caption_text for h in user_media]}")

    # tictoc crawler
    if False:
        crawler = Crawler("tictoc")
        ht_info = crawler.execute(hashtag_info="아저씨")
        ht_list = crawler.execute(hashtag_list="아저씨")
        ms_list = crawler.execute(music_list="행운음원-7224788594336992002")
        us_info = crawler.execute(user_info="user4rkmbsmyvh")
        with open("us_info.json", "w") as file:
            file.write(json.dumps(us_info))

    # TODO: 
    # 상품리뷰관련 - originProductNo 소재를 파악해야함
    # cat_id, frm 등 kwargs가 의미하는 바가 무엇인지
    # xpath로 가져오도록 변경
    if True:
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

    print("End!!")
