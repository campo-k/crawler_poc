from crawler_modules.c_crawler import *


if __name__ == "__main__":
    # instagram crawler
    if False:
        INSTA_USER_NAME = "lafefish@gmail.com"
        INSTA_USER_PASS = "jjang$194324"
        # Instagram open source crawler initialize.
        crawler = Crawler(
            "instagram", insta_id=INSTA_USER_NAME, insta_pw=INSTA_USER_PASS
        )
        # hashtag 관련
        ht_info = crawler.execute(hashtag_info="살로몬")
        ht_media_tops = crawler.execute(hashtag_media_top="살로몬")
        ht_media_rcts = crawler.execute(hashtag_media_rct="살로몬")  # user 관련
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

    # naver store crawler
    if True:
        crawler = Crawler("naver_store_keyword_info")
        crawler.execute()
        crawler = Crawler("naver_store_products")
        crawler.execute()
        crawler = Crawler("naver_store_product_reviews")
        crawler.execute()
        crawler = Crawler("naver_store_integrated_products")
        crawler.execute()

    # tictoc crawler
    if False:
        crawler = Crawler("tictoc")
        ht_info = crawler.execute(hashtag_info="아저씨")
        ht_list = crawler.execute(hashtag_list="아저씨")
        ms_list = crawler.execute(music_list="행운음원-7224788594336992002")
        us_info = crawler.execute(user_info="user4rkmbsmyvh")

    print("End!!")
