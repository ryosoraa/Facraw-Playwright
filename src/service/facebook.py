import asyncio
import random
import os
import json

from urllib import request
from uuid import uuid4
from tqdm import tqdm
from icecream import ic
from pyquery import PyQuery
from datetime import datetime
from time import time
from playwright.async_api import BrowserContext
from dotenv import load_dotenv
from tqdm import tqdm

from src.utils.Parser import Parser
from src.utils.File import File
from src.service.UrlParser import UrlParser
from src.utils.Logs import logger
from src.utils.named import vname


class Facebook:
    def __init__(self) -> None:

        self.TOTAL_FETCH_IMAGE_WORKERS = 2
        self.TOTAL_FETCH_CARD_WORKERS = 2

        self.__url_parser = UrlParser()
        self.__parser = Parser()
        self.__file = File()

        self.target_media = None

        self.search_url = 'https://www.facebook.com/search/groups/?q='
        self.base_url = 'https://www.facebook.com'


    def __curl(self, path: str,url_image: str):
        request.urlretrieve(url_image, path)


    def __url(self, path):
        with open(path, 'r', encoding='utf-8') as file:
            data: list = json.load(file)

        logger.info(f'data remaining: {len(data)}')
        print()

        if not len(data): return False

        url = data[0]
        data.remove(url)
        self.__file.write_json(path=path, content=data)

        return url
    

    def __build_cookies(self, cookies: str) -> str:
        formatted_cookies = ''
        for cookie in json.loads(cookies):
            formatted_cookies += f'{cookie["name"]}={cookie["value"]}; '

        
        return formatted_cookies.rstrip('; ').replace(' ', '')


    async def fetch_image(self, browser: BrowserContext, delay: int):
        page = await browser.new_page()
        page.set_default_timeout(120000)
        await page.set_viewport_size({"width":1919, "height":1050})

        for media in self.target_media:
            await asyncio.sleep(delay)
        
            while True:
                URL = self.__url(path=f'target/image/{media}')

                if not URL:
                    os.rmdir(f'target/image/{media}')
                    break

                await page.goto(url=URL)
                await page.wait_for_load_state('load', timeout=120000)

                await page.is_visible(selector='img.x85a59c.x193iq5w.x4fas0m.x19kjcj4')
                URL = PyQuery(await page.inner_html('#facebook')).find(selector='img.x85a59c.x193iq5w.x4fas0m.x19kjcj4').attr('src')

                if not URL:
                    ic('not found')
                    await asyncio.sleep(5)
                    URL = PyQuery(await page.inner_html('#facebook')).find(selector='img.x85a59c.x193iq5w.x4fas0m.x19kjcj4').attr('src')
                    await asyncio.sleep(5)

                self.__curl(path=f'data/image/{uuid4()}.jpg', url_image=URL)

        page.close()

    async def extract_image(self, browser: BrowserContext, cookie):
        page = await browser.new_page()
        page.set_default_timeout(120000)
        await page.set_viewport_size({"width":1919, "height":1050})

        while True:
            
            group: dict = self.__url(path='target/groups/groups.json')

            if not group: break
            if group['status'] == 'Private': continue
            

            URL = f'{group["url"]}media'

            await page.goto(URL)

            last = None
            while True:

                await page.evaluate("window.scrollTo(0, document.querySelector('#facebook div > div:nth-child(1) > div > div.x9f619.x1n2onr6.x1ja2u2z > div > div > div.x78zum5.xdt5ytf.x1t2pt76.x1n2onr6.x1ja2u2z.x10cihs4 > div.x78zum5.xdt5ytf.x1iyjqo2.x1us19tq > div > div.x9f619.x2lah0s.x1n2onr6.x78zum5.x1iyjqo2.x1t2pt76.x1lspesw > div > div > div.x78zum5.xdt5ytf.x1iyjqo2 > div > div > div > div > div > div > div').scrollHeight);")
                await asyncio.sleep(3)
                new_height = await page.evaluate("document.querySelector('#facebook div > div:nth-child(1) > div > div.x9f619.x1n2onr6.x1ja2u2z > div > div > div.x78zum5.xdt5ytf.x1t2pt76.x1n2onr6.x1ja2u2z.x10cihs4 > div.x78zum5.xdt5ytf.x1iyjqo2.x1us19tq > div > div.x9f619.x2lah0s.x1n2onr6.x78zum5.x1iyjqo2.x1t2pt76.x1lspesw > div > div > div.x78zum5.xdt5ytf.x1iyjqo2 > div > div > div > div > div > div > div').scrollHeight;")
                if last == new_height: break
                last = new_height


            group['url_cards'] = [f"{self.base_url}{PyQuery(card).attr('href')}" for card in tqdm(PyQuery(await page.inner_html('#facebook')).find(selector='div.x1qjc9v5.x1q0q8m5.x1qhh985.xu3j5b3.xcfux6l.x26u7qi.xm0m39n.x13fuv20.x972fbf.x1ey2m1c.x9f619.x78zum5.xds687c.xdt5ytf.x1iyjqo2.xs83m0k.x1qughib.xat24cr.x11i5rnm.x1mh8g0r.xdj266r.x2lwn1j.xeuugli.x18d9i69.x4uap5.xkhd6sd.xexx8yu.x10l6tqk.x17qophe.x13vifvy.x1ja2u2z a.x1i10hfl.x1qjc9v5.xjbqb8w.xjqpnuy.xa49m3k.xqeqjp1.x2hbi6w.x13fuv20.xu3j5b3.x1q0q8m5.x26u7qi.x972fbf.xcfux6l.x1qhh985.xm0m39n.x9f619.x1ypdohk.xdl72j9.x2lah0s.xe8uvvx.xdj266r.x11i5rnm.xat24cr.x1mh8g0r.x2lwn1j.xeuugli.xexx8yu.x4uap5.x18d9i69.xkhd6sd.x1n2onr6.x16tdsg8.x1hl2dhg.xggy1nq.x1ja2u2z.x1t137rt.x1o1ewxj.x3x9cwd.x1e5q0jg.x13rtm0m.x1q0g3np.x87ps6o.x1lku1pv.x1rg5ohu.x1a2a7pz'), \
                                    ascii=True, smoothing=0.1)]

            logger.info(f'total images obtained: {len(group["url_cards"])}')
            print()

            group['urls_images'] = [self.__url_parser.ex(path='data/image', image_id=id.split("fbid=")[1].split("&")[0], media_token=id.split("=")[-1], cookies=cookie, url_card=id) 
               for id in tqdm(group['url_cards'], ascii=True, smoothing=0.1, total=len(group['url_cards']))]
            
            print()
            logger.info(f'data saved in: data/json/{vname(group["name"])}.json')
            print()

            self.__file.write_json(path=f'data/json/{vname(group["name"])}.json', content=group)


    async def fetch_group(self, search: str, browser: BrowserContext):
        page = await browser.new_page()
        page.set_default_timeout(120000)
        await page.set_viewport_size({"width":1919, "height":1050})

        URL = self.search_url+search

        await page.goto(url=URL)
        await asyncio.sleep(10)

        for _ in range(5):
            await page.evaluate("window.scrollTo(0, document.querySelector('#facebook div > div.x9f619.x1n2onr6.x1ja2u2z.xdt5ytf.x193iq5w.xeuugli.x1r8uery.x1iyjqo2.xs83m0k.x78zum5.x1t2pt76 > div > div > div > div > div').scrollHeight)")
            await asyncio.sleep(3)
            

        cards = PyQuery(await page.inner_html(selector='#facebook')).find('body div > div.x9f619.x1n2onr6.x1ja2u2z div.x78zum5.xdt5ytf.x1t2pt76.x1n2onr6.x1ja2u2z.x10cihs4 > div.x9f619.x2lah0s.x1nhvcw1.x1qjc9v5.xozqiw3.x1q0g3np.x78zum5.x1iyjqo2.x1t2pt76.x1n2onr6.x1ja2u2z.x1h6rjhl > div.x9f619.x1n2onr6.x1ja2u2z.xdt5ytf.x193iq5w.xeuugli.x1r8uery.x1iyjqo2.xs83m0k.x78zum5.x1t2pt76  > div  div.x6s0dn4.xkh2ocl.x1q0q8m5.x1qhh985.xu3j5b3.xcfux6l.x26u7qi.xm0m39n.x13fuv20.x972fbf.x9f619.x78zum5.x1q0g3np.x1iyjqo2.xs83m0k.x1qughib.xat24cr.x11i5rnm.x1mh8g0r.xdj266r.x2lwn1j.xeuugli.x18d9i69.x4uap5.xkhd6sd.xexx8yu.x1n2onr6.x1ja2u2z')

        results = [
            {
                'crawling_time': str(datetime.now()),
                'crawling_time_epoch': int(time()),
                'url': self.__parser.ex(html=component, selector='div.xu06os2.x1ok221b:nth-child(1) a').attr('href'),
                'name': self.__parser.ex(html=component, selector='a').text(),
                'status': self.__parser.ex(html=component, selector='div.xu06os2.x1ok221b:nth-child(2)').text().split(' · ')[0],
                'members': self.__parser.ex(html=component, selector='div.xu06os2.x1ok221b:nth-child(2)').text().split(' · ')[1],
                'post': self.__parser.ex(html=component, selector='div.xu06os2.x1ok221b:nth-child(2)').text().split(' · ')[-1],

             }for component in cards
        ]

        logger.info(f'Total Groups Found: {len(results)}')
        logger.info(f'Update Groups target')
        print()

        
        self.__file.write_json(path='target/groups/groups.json', content=results)

        await page.close()

    async def main(self, browser: BrowserContext, cookies: str, search: str):
        

        TARGET_GROUPS = len(self.__file.read_json('target/groups/groups.json'))

        if not TARGET_GROUPS:
            await asyncio.create_task(self.fetch_group(browser=browser, search=search))

        logger.info(f'do a group fetch with the search keyword: {search}')
        logger.info(f'Total Target Groups: {TARGET_GROUPS}')
        print()

        logger.info('image fetch preparation')
        logger.info(f'Total Workers: {self.TOTAL_FETCH_CARD_WORKERS}')
        print()

        tasks = asyncio.create_task(self.extract_image(browser=browser, cookie=self.__build_cookies(cookies=cookies)))
        await tasks
        
        # tasks = [asyncio.create_task(self.fetch_image(browser=browser, delay=worker)) for worker in self.TOTAL_FETCH_IMAGE_WORKERS]
        # await asyncio.gather(*tasks)

        
        logger.info('facebook scraper completed')

        return True

