from crawler_modules.c_crawler import *


if __name__ == "__main__":
    crawler = Crawler("naver_store_keyword_info")
    crawler.execute()

    crawler = Crawler("naver_store_products")
    crawler.execute()
    
    crawler = Crawler("naver_store_product_reviews")
    crawler.execute()

    crawler = Crawler("naver_store_integrated_products")
    crawler.execute()

    # unavailable
    # crawler = Crawler("naver_store_integrated_reviews")
    # crawler.execute()
    