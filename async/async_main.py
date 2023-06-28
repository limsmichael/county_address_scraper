import asyncio
import time

from selenium.common import TimeoutException

import selenium_helpers
from getter import Getter
from consumer import Consumer
from selenium import webdriver


async def main():
    start = time.time()
    getter = Getter('../Addresses.csv')
    n_workers = 0
    driver = webdriver.Chrome()
    handles = [driver.current_window_handle]
    for worker in range(n_workers):
        driver.switch_to.new_window()
        handles.append(driver.current_window_handle)
    consumers = [Consumer(getter.single_unit_df, getter.multi_unit_df, driver, handle) for handle in handles]
    consumers[0].driver.get(consumers[0].baseurl)
    try:
        selenium_helpers.clear_load_window(consumers[0].driver, consumers[0].baseurl)
    except TimeoutException:
        pass
    queue = asyncio.Queue()
    getter_task = asyncio.create_task(getter.run(queue))
    await asyncio.sleep(0.1)
    workers = [asyncio.create_task(consumer.run(queue)) for consumer in consumers]
    await queue.join()
    getter_task.cancel()
    for worker in workers:
        worker.cancel()
    print(f'total elapsed: {time.time() - start}')




if __name__ == "__main__":
    asyncio.run(main())