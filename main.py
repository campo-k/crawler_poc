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
