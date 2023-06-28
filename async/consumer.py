import asyncio
import os.path
import re
import time

import pandas as pd
import selenium
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

import selenium_helpers
from selenium.common.exceptions import TimeoutException, NoSuchElementException


class Consumer:
    def __init__(self, single_unit_df: pd.DataFrame, multi_unit_df: pd.DataFrame, driver: selenium.webdriver.Chrome,
                 handle):
        self.single_unit_df = single_unit_df
        self.multi_unit_df = multi_unit_df
        self.handle = handle
        self.driver = driver
        self.driver.switch_to.window(self.handle)
        self.baseurl = "https://property.spatialest.com/nc/brunswick#/property/220JB011"
        if not os.path.exists('./single_unit_compiled.csv'):
            self.single_unit_df.to_csv('./single_unit_compiled.csv')
        if not os.path.exists('./multi_unit_compiled.csv'):
            self.multi_unit_df.to_csv('./multi_unit_compiled.csv')
        self.single_mode = True

    async def get_single_parcel(self, value_to_check, idx):
        replaced = value_to_check.replace(" ", "%20")
        url = f'https://property.spatialest.com/nc/brunswick#/search?term={replaced}&page=1'
        await selenium_helpers.get_url(self.driver, url)
        parcel = self.driver.current_url[-8:]
        self.single_unit_df = pd.read_csv('./single_unit_compiled.csv', index_col="Unnamed: 0")
        self.single_unit_df.loc[idx, 'Parcel'] = str(parcel)
        self.single_unit_df.to_csv('./single_unit_compiled.csv')

    async def get_multi_parcel_search(self, value_to_check):
        replaced = value_to_check.replace(" ", "%20")
        url = f'https://property.spatialest.com/nc/brunswick#/search?term={replaced}&page=1'
        await selenium_helpers.get_url(self.driver, url)
        wait = WebDriverWait(self.driver, 2)
        rows = wait.until(EC.presence_of_element_located((By.CLASS_NAME, "col-12.results-list.grid")))
        parcels = list()
        parcels.append([parcel[:8] for parcel in rows.text.split("Parcel ID")[1:]])
        try:
            while self.driver.find_element(By.CLASS_NAME, 'pagination-container'):
                url = url[:-1] + str(int(url[-1]) + 1)
                await selenium_helpers.get_url(self.driver, url)
                # await(0.1)
                rows = wait.until(EC.presence_of_element_located((By.CLASS_NAME, "col-12.results-list.grid")))
                # parcel_idxs = [m.start() for m in re.finditer('Parcel ID', rows.text)]
                # tmp = [rows.text[parcel_idx + 9:parcel_idx + 17] for parcel_idx in parcel_idxs]
                tmp = [parcel[:8] for parcel in rows.text.split("Parcel ID")[1:]]
                parcels.append(tmp)
        except NoSuchElementException:
            print("Next page not found, continuing")
            pass
        except Exception as e:
            print(e)
            pass
        parcels = [val for sublist in parcels for val in sublist]
        return parcels

    async def associate_parcels(self, value_to_check, parcels):
        self.multi_unit_df = pd.read_csv('./multi_unit_compiled.csv', index_col="Unnamed: 0")
        df = self.multi_unit_df.loc[self.multi_unit_df["ST_ADDR_UNITLESS"] == value_to_check]
        df.sort_values("UNIT_NO", inplace=True)
        try:
            df["Parcel"].iloc[:len(parcels)] = parcels
            self.multi_unit_df.loc[df.index] = df
            self.multi_unit_df.to_csv('./multi_unit_compiled.csv')
        except Exception as e:
            print(e)

    async def run(self, queue: asyncio.Queue):
        while True:
            try:
                await self.process_work(queue)
            except asyncio.CancelledError:
                self.driver.close()
                self.driver.quit()
                return

    async def process_work(self, queue: asyncio.Queue):
        entry, idx = await queue.get()
        self.driver.switch_to.window(self.handle)
        # print(self.handle)
        try:
            if type(entry) == pd.Series:
                df_entry = entry
                value_to_check = f'{df_entry["ST_NUMB"]} {df_entry["ST_NAME"]}'
                self.single_mode = True
                if (self.single_unit_df.loc[idx, 'Parcel'] == "") or str(
                        (self.single_unit_df.loc[idx, 'Parcel']) == "nan"):
                    await self.get_single_parcel(value_to_check, idx)
                    print(f'Got parcel: {value_to_check}')
                else:
                    print(f'Parcel already exists: {df_entry["ST_NUMB"]} {df_entry["ST_NAME"]} {df_entry["UNIT_NO"]}')
            elif type(entry) == str:
                self.single_mode = False
                parcels = await self.get_multi_parcel_search(entry)
                await self.associate_parcels(entry, parcels)
        except Exception as e:
            # add error handling for addresses
            print(e, idx)
            pass
        queue.task_done()
