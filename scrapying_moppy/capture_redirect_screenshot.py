import asyncio
from playwright.async_api import TimeoutError, async_playwright
from datetime import datetime
import sys

result = []


async def scrape_moppy_ranking(filepath):
    async with async_playwright() as p:
        with open(filepath, 'r') as f:
            browser = await p.chromium.launch()
            page = await browser.new_page(is_mobile=True, user_agent='Mozilla/5.0 (iPhone; CPU iPhone OS 14_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0.3 Mobile/15E148 Safari/604.1')
            for url in f.readlines():
                u = url.rstrip()
                if u == '':
                    continue
                # ブラウザを起動し、ページにアクセスする
                try:
                    await page.goto(u, timeout=3000)
                    p = datetime.now().time()
                    await page.screenshot(path='{}.png'.format(p))
                    _url = page.url
                    print(_url)
                except TimeoutError:
                    print("error", u)
                    continue

            await browser.close()


asyncio.run(scrape_moppy_ranking(sys.argv[1]))
