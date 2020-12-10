import os
import dotenv

from scrapy.crawler import CrawlerProcess
from scrapy.settings import Settings

from gb_parse import settings

from gb_parse.spiders.autoyoula import AutoyoulaSpider
from gb_parse.spiders.hhru import HhruSpider
from gb_parse.spiders.instagram import InstagramSpider

if __name__ == '__main__':
    dotenv.load_dotenv('.env')
    
    crawl_settings = Settings()
    crawl_settings.setmodule(settings)

    crawl_proc = CrawlerProcess(settings=crawl_settings)

    #crawl_proc.crawl(AutoyoulaSpider)
    #crawl_proc.crawl(HhruSpider)

    hash_tags = ['python', 'code']
    crawl_proc.crawl(InstagramSpider, tags=hash_tags, login=os.getenv('INST_LOGIN'), enc_password=os.getenv('INST_PSWD'))

    crawl_proc.start()