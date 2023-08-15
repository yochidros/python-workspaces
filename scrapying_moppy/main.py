import asyncio
from playwright.async_api import async_playwright
import csv
import sys
import os

result = []


async def scrape_moppy_ranking(output):
    async with async_playwright() as p:
        # ブラウザを起動し、ページにアクセスする
        browser = await p.chromium.launch()
        page = await browser.new_page()
        await page.goto('https://ssl.pc.moppy.jp/login/')

        # ログイン情報を入力する
        await page.fill('input[name=\"mail\"]', os.environ['MOPPY_USERNAME'])
        await page.fill('input[name=\"pass\"]', os.environ['MOPPY_PASSWORD'])
        await page.locator('button.a-btn__login').click()

        # ログインが完了するまで待機する
        await page.wait_for_selector('#global-header')

        # ランキング情報を表す要素を特定する
        await page.goto('https://pc.moppy.jp/shopping/?schedule_sort=1&category_sort=2')
        categories = await page.query_selector('#js-slick__tab')
        genres = await categories.query_selector_all('.slick-slide')
        genre_items = []
        for genre in genres:
            text = await genre.get_attribute('data-ga-label')
            index = await genre.get_attribute('data-slick-index')
            genre_items.append((text, index))


        ranking_items = await page.query_selector_all('.m-ranking-category__inner')
        basic_items = []
        for ranking in ranking_items:
            current_genre_index = await ranking.get_attribute('data-slick-index')
            items = await ranking.query_selector_all('.block__link')
            for item in items:
                rank_number = await item.query_selector('.m-item__ranking')
                ranking = await rank_number.text_content()
                title = await item.get_attribute('data-ga-label')
                detail_link = await item.get_attribute('href')
                # print(ranking.strip(), title, detail_link)
                for genre in genre_items:
                    genre_title, genre_index = genre
                    if genre_index == current_genre_index:
                        basic_items.append(
                                (ranking.strip(), title, detail_link, genre_title, genre_index)
                                )

        for item in basic_items:
            ranking, title, link, category, c_index = item
            await page.goto(link)
            await page.wait_for_selector('.m-item__info__wrapper')
            timing_items = await page.query_selector_all('.m-item__define__timing')
            pre_timing = ''
            timing = ''
            if len(timing_items) == 1:
                now = timing_items[0]
                # _t = await now.query_selector('a')
                # t = await _t.get_attribute('data-ga-label')
                _v = await now.query_selector('dd >> nth=1')
                timing = await _v.text_content()
            elif len(timing_items) == 2:
                pre = timing_items[0]
                # _t = await pre.query_selector('a')
                # pt = await _t.get_attribute('data-ga-label')
                _v = await pre.query_selector('.a-item__define__timing--body')
                pre_timing = await _v.text_content()
                now = timing_items[1]
                # _t = await now.query_selector('a')
                # t = await _t.get_attribute('data-ga-label')
                _v = await now.query_selector('dd >> nth=1')
                timing = await _v.text_content()

            consider_text = ''
            _con = await page.query_selector('.a-item__consider')
            if _con is not None:
                consider = await _con.text_content()
                consider_text = consider.strip('昨日').strip('人のユーザーがこの広告を閲覧しました！')

            _point = await page.query_selector('.a-item__point--now')
            point = await _point.text_content()
            result.append(
                    (category, ranking, title, link, pre_timing, timing, point, consider_text)
                    )

            # 詳細画面を閉じる
            await page.go_back()

        await browser.close()

        with open('./{}.csv'.format(output), 'w') as f:
            fieldnames = ['category', 'ranking', 'title', 'link', 'consider_people', 'pre-timing', 'timing', 'point']
            writer = csv.DictWriter(f, fieldnames)
            writer.writeheader()
            data = []
            for v in result:
                category, ranking, title, link, pre_timing, timing, point, consider = v
                _v = {
                    'category': category,
                    'ranking': ranking,
                    'title': title,
                    'link': link,
                    'consider_people': consider,
                    'pre-timing': pre_timing,
                    'timing': timing,
                    'point': point
                }
                data.append(_v)

            writer.writerows(data)

        print('🎉 done!!')


asyncio.run(scrape_moppy_ranking(sys.argv[1]))

