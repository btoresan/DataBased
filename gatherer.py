from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.firefox import GeckoDriverManager  
from datetime import datetime

import asyncio

async def gather_protondb_async(urls, batch_size):
    batches = [urls[i:i+batch_size] for i in range(0, len(urls), batch_size)] 
    tasks = []

    for batch in batches:
        task = asyncio.to_thread(gather_protondb, batch)
        tasks.append(task)

    await asyncio.gather(*tasks)
        
def gather_protondb(urls):
    gecko_path = '/home/nickyecen/.wdm/drivers/geckodriver/linux64/v0.35.0/geckodriver'
    driver = webdriver.Firefox(service=Service(gecko_path))
    data = [scrape_protondb(driver, url) for url in urls]
    driver.quit()

    return data

def scrape_protondb(driver, url):
    driver.get(url)

    try:
        # Wait for the element to be present for up to 10 seconds
        wait = WebDriverWait(driver, 10)

        title_element = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "span[class^='GameInfo__']")))
        title = title_element.text

        medal_element = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "span[class^='MedalSummary__']")))
        medal = medal_element.text
        
        wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "div.styled__Flex-sc-g24nyo-0.styled__Row-sc-g24nyo-4.styled__AlignedRow-sc-g24nyo-7.DeckVerifiedInfo__AlignedRowWidthUnset-sc-acfn33-0.gMlTmq.dKXMgt.kYZFue.dxRxb")))
        deck_container = driver.find_element(By.CSS_SELECTOR, "div.styled__Flex-sc-g24nyo-0.styled__Row-sc-g24nyo-4.styled__AlignedRow-sc-g24nyo-7.DeckVerifiedInfo__AlignedRowWidthUnset-sc-acfn33-0.gMlTmq.dKXMgt.kYZFue.dxRxb")
        deck = deck_container.find_elements(By.TAG_NAME, "span")[1].text

        wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "div.styled__Flex-sc-g24nyo-0.styled__Row-sc-g24nyo-4.styled__AlignedRow-sc-g24nyo-7.ChromebookReadyInfo__AlignedRowWidthUnset-sc-92d0dc-0.gMlTmq.dKXMgt.kYZFue.bcGSMK")))
        chromebook_container = driver.find_element(By.CSS_SELECTOR, "div.styled__Flex-sc-g24nyo-0.styled__Row-sc-g24nyo-4.styled__AlignedRow-sc-g24nyo-7.ChromebookReadyInfo__AlignedRowWidthUnset-sc-92d0dc-0.gMlTmq.dKXMgt.kYZFue.bcGSMK")
        chromebook = chromebook_container.find_elements(By.TAG_NAME, 'span')[1].text

        return {
                'id': url.split('/')[-1],
                'title': title,
                'medal': medal,
                'deck': deck,
                'chromebook': chromebook
                }

    except Exception as e:
        print(url.split('/')[-1], e)

# Example usage:
t = ['https://www.protondb.com/app/240', 'https://www.protondb.com/app/550', 'https://www.protondb.com/app/444090',
                'https://www.protondb.com/app/387990', 'https://www.protondb.com/app/227940', 'https://www.protondb.com/app/460930',
                'https://www.protondb.com/app/379720', 'https://www.protondb.com/app/440', 'https://www.protondb.com/app/221100']
t *= 10

init = datetime.now()
asyncio.run(gather_protondb_async(t, 25))
print(datetime.now() - init)

