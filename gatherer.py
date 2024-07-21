import asyncio

from playwright.async_api import async_playwright
from bs4 import BeautifulSoup

def get_html_data(html):
    soup = BeautifulSoup(html, 'html.parser')
    
    title_html = soup.select_one('[class^=GameInfo]')
    medal_html = soup.select_one('[class^=MedalSummary]')
    deck_verified_html = soup.find('div', class_='styled__Flex-sc-g24nyo-0 styled__Row-sc-g24nyo-4 styled__AlignedRow-sc-g24nyo-7 DeckVerifiedInfo__AlignedRowWidthUnset-sc-acfn33-0 gMlTmq dKXMgt kYZFue dxRxb')
    chromebook_ready_html = soup.find('div', class_='styled__Flex-sc-g24nyo-0 styled__Row-sc-g24nyo-4 styled__AlignedRow-sc-g24nyo-7 ChromebookReadyInfo__AlignedRowWidthUnset-sc-92d0dc-0 gMlTmq dKXMgt kYZFue bcGSMK')
   
    title = title_html.text.strip()
    medal = medal_html.text.strip()
    deck_verified = deck_verified_html.find_all('span')[1].text.strip()
    chromebook_ready = chromebook_ready_html.find_all('span')[-1].text.strip()

    return {'title': title, 'medal': medal, 'deck_verified': deck_verified, 'chromebook_ready': chromebook_ready}

async def get_game_html(game_id):
    url = 'https://www.protondb.com/app/' + str(game_id)

    async with async_playwright() as pw:
        browser = await pw.chromium.launch(headless=True)
        page = await browser.new_page()
        await page.goto(url)        
        await page.wait_for_load_state('networkidle')
        html = await page.content()
        await page.close()
        return html    

async def gather_game_data(game_id):
    print(f'Started data gathering for {game_id}')
    html = await get_game_html(game_id)
    data = get_html_data(html)
    print(f'Finished data gathering for {game_id}')

    return (game_id, data)

async def gather_gamelist_data(game_ids):
    tasks = []
    for game_id in game_ids:
        tasks.append(gather_game_data(game_id))
    results = await asyncio.gather(*tasks)

    data = {}
    for result in results:
        data[result[0]] = result[1]

    return data

print(asyncio.run(gather_gamelist_data([346110,413150, 10, 1174180, 264710, 779340, 552520, 391540, 620, 356190])))
