import asyncio
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


def clear_load_window(driver: webdriver, url):
    driver.get(url)
    wait = WebDriverWait(driver,3)
    button = wait.until(EC.element_to_be_clickable((By.CLASS_NAME, 'submitButton.btn.btn-primary')))
    button.click()

async def input_property(driver, url, property):
    # driver.get(url)
    wait = WebDriverWait(driver, 5)
    text_box = wait.until(EC.presence_of_element_located((By.ID, "primary_search")))
    text_box.clear()
    text_box.send_keys(property)
    css_path = '#rct-main-app > div.main-app.container-fluid.py-2 > ' \
               'div.search-navigation.container.mb-2.d-print-none > ' \
               'div > div.searchbar.row > div.col-12.order-md-2.order-1.col-md-8 > ' \
               'div > div.search-text.col-10.pb-md-0.pb-2.pr-0 > div > div.search-bar-input-container > ' \
               'div > ul > li:nth-child(1) > ul > li:nth-child(1) > a'
    suggestion = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, css_path)))
    suggestion.click()
    asyncio.sleep(0.2)
    # css_path = '#prccontent > div > section > div > div.media > div > ' \
    #            'div > div:nth-child(1) > div > div > div > img'
    # wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, css_path)))

async def get_url(driver, url):
    wait = WebDriverWait(driver, 5)
    driver.get(url)
    # await wait.until(EC.presence_of_element_located((By.CLASS_NAME, "image-wrapper")))
    await asyncio.sleep(0.1)
    try:
        while not wait.until(EC.presence_of_element_located((By.CLASS_NAME, "image-wrapper"))):
            await asyncio.sleep(0.1)
    except:
        while not wait.until(EC.presence_of_element_located((By.CLASS_NAME, "col-12.results-list.grid"))):
            await asyncio.sleep(0.1)
