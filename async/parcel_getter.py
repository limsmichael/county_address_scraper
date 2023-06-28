import asyncio

import pandas as pd
import requests
from selenium.webdriver.common.by import By

import file_helpers
from selenium import webdriver
import selenium_helpers


class ParcelGetter:
    def __init__(self, n_workers):
        self.curr_val = 0
        self.n_workers = n_workers
        self.queue = asyncio.Queue()
        self.single_unit_df, self.multi_unit_df = file_helpers.csv_to_df("../Addresses.csv")
        self.baseurl = "https://property.spatialest.com/nc/brunswick#/property/220JB011"
        self.driver = webdriver.Chrome()
        self.seen = pd.DataFrame()
        self.single_mode = True
        # self.baseurl = 'https://property.spatialest.com/nc/brunswick/api/v1/recordcard/'

    async def run(self):
        selenium_helpers.clear_load_window(self.driver, self.baseurl)
        await self.get_next_parcel()
        workers = [asyncio.create_task(self.parcel_worker()) for _ in range(self.n_workers)]
        await self.queue.join()
        for worker in workers:
            worker.cancel()

    async def get_next_parcel(self):
        for value in range(self.single_unit_df.shape[0]):
            parcel = self.single_unit_df.iloc[value]
            index = self.single_unit_df.index[value]
            await self.queue.put((parcel, index))
            self.curr_val=value


    async def parcel_worker(self):
        while True:
            try:
                await self.process_work()
            except asyncio.CancelledError:
                return

    async def process_work(self):
        df_entry, idx = await self.queue.get()
        if self.single_unit_df.loc[idx, 'Parcel'] == "":
            if str(df_entry["UNIT_NO"]) == 'nan':
                value_to_check = f'{df_entry["ST_NUMB"]} {df_entry["ST_NAME"]}'
            else:
                value_to_check = f'{df_entry["ST_NUMB"]} {df_entry["ST_NAME"]} {df_entry["UNIT_NO"]}'
            try:
                selenium_helpers.input_property(self.driver,self.baseurl, value_to_check)
                parcel = self.driver.current_url[-8:]
                if self.single_mode:
                    self.single_unit_df.loc[idx, 'Parcel'] = parcel
                    self.single_unit_df.to_csv('./single_unit_compiled.csv')
                else:
                    self.single_unit_df.loc[idx, 'Parcel'] = parcel
                    self.multi_unit_df.to_csv('./multi_unit_compiled.csv')
                print(f'Got parcel: {value_to_check}')
                await self.get_next_parcel()
            except Exception as e:
                # add error handling for addresses
                print(e, idx)
                pass
        else:
            print(f'Parcel already exists: {df_entry["ST_NUMB"]} {df_entry["ST_NAME"]} {df_entry["UNIT_NO"]}')
        self.queue.task_done()



if __name__ == "__main__":
    async def main():
        getter = ParcelGetter(100)
        await getter.run()


    asyncio.run(main(), debug=True)
