from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.firefox import GeckoDriverManager  
from datetime import datetime
from functools import reduce

import asyncio
import aiohttp

# scrape_for: list int -> dict
# obj.: given a list of steam app ids and a number of browsers to search in, gathers
# title, medal, developer, release date, and steam deck and chromebook ready flags and
# returns it parsed in a dictionary by id
async def scrape_for(game_ids, num_windows):
    protondb_urls = [('https://www.protondb.com/app/' + str(game_id)) for game_id in game_ids]

    steam_tasks = []
    async with aiohttp.ClientSession() as session:
        for game_id in game_ids:
            steam_tasks.append(scrape_steam(session, game_id))

        gather_task = gather_async(protondb_urls, num_windows, scrape_protondb)
        steamdb_data = await asyncio.gather(*steam_tasks)

    print('Closed session')
    protondb_data = await gather_task

    steamdb_data.sort(key=lambda x: x[0])
    protondb_data.sort(key=lambda x: x[0])

    dataset = {}
    for s, p in zip(steamdb_data, protondb_data):
        print(s, p, s[1], p[1])
        print(s[1] | p[1])
        dataset[s[0]] = s[1] | p[1]

    return dataset

# gather_async: list num fun -> list
# obj.: given a list of urls, the number of browser windows do gather from,
# and the gatherer function, gathers the data from the function asychronously
async def gather_async(urls, num_windows, func):

    # Divides urls in batches for each window
    batch_size = len(urls) // num_windows + 1
    batches = [urls[i:i+batch_size] for i in range(0, len(urls), batch_size)] 
    tasks = []

    # Gathers data from each batch
    for batch in batches:
        task = asyncio.to_thread(gatherer, batch, func)
        tasks.append(task)

    l = await asyncio.gather(*tasks)

    return reduce(lambda x, y: x + y, l)
      
# gatherer: list fun -> list
# obj.: given a list of urls and a scraper function, scrapes from the urls for data
def gatherer(urls, func):
    gecko_path = '/home/nickyecen/.wdm/drivers/geckodriver/linux64/v0.35.0/geckodriver'
    driver = webdriver.Firefox(service=Service(gecko_path))
    data = [func(driver, url) for url in urls]
    driver.quit()

    return data

# scrape_steam: driver string -> tuple 
# obj.: given a driver browser and a steamDB url, gathers the developer and release date of a game
async def scrape_steam(session, app_id):
    url = f'https://store.steampowered.com/api/appdetails?appids={app_id}'

    try:
        async with session.get(url) as response:
            data = await response.json()

            if data[str(app_id)]['success']:
                game_data = data[str(app_id)]['data']
                developer = game_data.get('developers', ['N/A'])[0]
                release = game_data.get('release_date', {}).get('date', 'N/A')

                date_format = '%d %b, %Y'
                release = int(datetime.strptime(release, date_format).timestamp())

                return int(app_id), {
                                'developer': developer,
                                'release': release
                                }

    except Exception as e:
        print(url.split('=')[-1], e)

# scrape_protondb: driver string -> tuple 
# obj.: given a driver browser and a protondb url, gathers the title, medal, and
# steam deck and chromebook verified flags
def scrape_protondb(driver, url):
    driver.get(url)

    try:
        # Wait for page to load
        wait = WebDriverWait(driver, 30)

        # Gets title
        title_element = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "span[class^='GameInfo__']")))
        title = title_element.text

        # Gets medal
        medal_element = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "span[class^='MedalSummary__']")))
        medal = medal_element.text
       
        # Gets steamdeck verified flag
        wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "div.styled__Flex-sc-g24nyo-0.styled__Row-sc-g24nyo-4.styled__AlignedRow-sc-g24nyo-7.DeckVerifiedInfo__AlignedRowWidthUnset-sc-acfn33-0.gMlTmq.dKXMgt.kYZFue.dxRxb")))
        deck_container = driver.find_element(By.CSS_SELECTOR, "div.styled__Flex-sc-g24nyo-0.styled__Row-sc-g24nyo-4.styled__AlignedRow-sc-g24nyo-7.DeckVerifiedInfo__AlignedRowWidthUnset-sc-acfn33-0.gMlTmq.dKXMgt.kYZFue.dxRxb")
        deck = deck_container.find_elements(By.TAG_NAME, "span")[1].text

        # Gets chromebook ready flag
        wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "div.styled__Flex-sc-g24nyo-0.styled__Row-sc-g24nyo-4.styled__AlignedRow-sc-g24nyo-7.ChromebookReadyInfo__AlignedRowWidthUnset-sc-92d0dc-0.gMlTmq.dKXMgt.kYZFue.bcGSMK")))
        chromebook_container = driver.find_element(By.CSS_SELECTOR, "div.styled__Flex-sc-g24nyo-0.styled__Row-sc-g24nyo-4.styled__AlignedRow-sc-g24nyo-7.ChromebookReadyInfo__AlignedRowWidthUnset-sc-92d0dc-0.gMlTmq.dKXMgt.kYZFue.bcGSMK")
        chromebook = chromebook_container.find_elements(By.TAG_NAME, 'span')[1].text

        return int(url.split('/')[-1]), {
                                    'title': title,
                                    'medal': medal,
                                    'deck': deck,
                                    'chromebook': chromebook
                                    }

    except Exception as e:
        print(url.split('/')[-1], e)

# Example usage:
t0 = ['https://steamdb.info/app/1119730/']
t1 = ['https://www.protondb.com/app/240', 'https://www.protondb.com/app/550', 'https://www.protondb.com/app/444090',
                'https://www.protondb.com/app/387990', 'https://www.protondb.com/app/227940', 'https://www.protondb.com/app/460930',
                'https://www.protondb.com/app/379720', 'https://www.protondb.com/app/440', 'https://www.protondb.com/app/221100']
#t *= 10

init = datetime.now()
print(asyncio.run(scrape_for([1119370, 240, 550, 444090, 387990, 227940, 460930, 379720, 440, 221100], 4)))
print(datetime.now() - init)

