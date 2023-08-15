import asyncio
from playwright.async_api import TimeoutError, async_playwright
import sys

result = []


async def scrape_moppy_ranking(urllist_filename):
    filepath = urllist_filename
    async with async_playwright() as p:
        with open(filepath) as f:
            browser = await p.chromium.launch()
            page = await browser.new_page(
                    is_mobile=True,
                    user_agent='Mozilla/5.0 (iPhone; CPU iPhone OS 14_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0.3 Mobile/15E148 Safari/604.1'
                    )
            for url in f.readlines():
                u = url.rstrip()
                if u == '':
                    continue
                try:
                    await page.goto(u, timeout=3000)
                    _url = page.url
                    print(_url)
                except TimeoutError:
                    print("error", u)
                    continue

            await browser.close()

if __name__ == '__main__':
    asyncio.run(scrape_moppy_ranking(sys.argv[1]))

