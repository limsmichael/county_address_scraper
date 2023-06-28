import re
import time
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


def tax_csv_to_df(csv_path: str) -> pd.DataFrame:
    with open(csv_path) as f:
        df = pd.read_csv(f)
    df = df.loc[df['City'] == "BALD HEAD ISLAND"]
    df = df.rename(columns={df.columns[0]: "OBJECTID"})
    df = df.reset_index()

    return df

def csv_to_df(csv_path: str) -> pd.DataFrame:
    with open(csv_path) as f:
        df = pd.read_csv(f)
    df = df.loc[df['CITY'] == "BHI"]
    df = df.rename(columns={df.columns[0]: "X"})
    # df = df.reset_index()
    df["Parcel"]=''
    single_unit_df = df.loc[(df['UNIT_NO'] == " ") | (df['UNIT_NO'].isnull())]
    multi_unit_df = df.loc[(df['UNIT_NO'] != " ") & (~df['UNIT_NO'].isnull()) & (df['UNIT_NO']!="POOL")]
    multi_unit_df["ST_ADDR_UNITLESS"] = [f'{multi_unit_df["ST_NUMB"].iloc[row]} {multi_unit_df["ST_NAME"].iloc[row]}' for row in range(len(multi_unit_df))]

    return single_unit_df, multi_unit_df



def get_owner_name(owner_info):
    owner_info = owner_info.replace("\n", " ")
    splits = re.split(r',|!|;|-', owner_info)
    if "llc" in splits[0].lower():
        return [splits[0], " "]
    else:
        return splits[0].split()[:2]


def get_mailing_address(owner_info):
    owner_info = owner_info.replace("\n", " ")
    splits = re.split(r',|!|;|-', owner_info)
    # validate if splits[1] is an address
    is_addr = False
    num_idx = 0
    curr_splits = splits[1].split()
    for idx, split in enumerate(curr_splits):
        try:
            int(split)
            is_addr = True
            num_idx = idx
            try:
                int(curr_splits[idx + 1])
                num_idx = idx + 1
            except:
                pass
            break
        except:
            pass
    if is_addr:
        addr_splits = curr_splits[num_idx:]
        for idx in range(0, num_idx):
            addr_splits.append(curr_splits[idx])
    elif splits[1] == ' ':
        addr_splits = splits[2].split()
    elif splits[2] == ' ':
        addr_splits = splits[3].split()

    str_num = addr_splits[0]
    str_name = ""
    for subsplit in addr_splits[1:]:
        str_name += subsplit + " "
    str_name = str_name[:-1]
    city = splits[-3]
    state = splits[-2]
    zip_code = splits[-1]
    return [str_num, str_name, city, state, zip_code]


def input_property_info(driver, curr_property, search_col = "ST_ADDR"):
    text_box = driver.find_element(By.ID, "primary_search")
    text_box.clear()
    if type(curr_property) is pd.Series:
        text_box.send_keys(curr_property[search_col])
    else:
        text_box.send_keys(curr_property)

    try:
        if type(curr_property) is pd.Series:
            search_text = curr_property[search_col]
            # css_path = '#rct-main-app > div.main-app.container-fluid.py-2 > div.search-navigation.container.mb-2.d-print-none > div > div.searchbar.row > div.col-12.order-md-2.order-1.col-md-8 > div > div.search-text.col-10.pb-md-0.pb-2.pr-0 > div > div.search-bar-input-container > div > ul > li:nth-child(2) > ul > li'
            if search_col == "ST_ADDR":
                css_path = '#rct-main-app > div.main-app.container-fluid.py-2 > div.search-navigation.container.mb-2.d-print-none > div > div.searchbar.row > div.col-12.order-md-2.order-1.col-md-8 > div > div.search-text.col-10.pb-md-0.pb-2.pr-0 > div > div.search-bar-input-container > div > ul > li:nth-child(2) > ul > li:nth-child(1) > a > strong'
            else:
                css_path = '#rct-main-app > div.main-app.container-fluid.py-2 > div.search-navigation.container.mb-2.d-print-none > div > div.searchbar.row > div.col-12.order-md-2.order-1.col-md-8 > div > div.search-text.col-10.pb-md-0.pb-2.pr-0 > div > div.search-bar-input-container > div > ul > li:nth-child(2) > ul > li > a > strong'
        else:
            search_text = curr_property
            try:
                # css_path = '#rct-main-app > div.main-app.container-fluid.py-2 > div.search-navigation.container.mb-2.d-print-none > div > div.searchbar.row > div.col-12.order-md-2.order-1.col-md-8 > div > div.search-text.col-10.pb-md-0.pb-2.pr-0 > div > div.search-bar-input-container > div > ul > li:nth-child(1) > ul > li:nth-child(1)'
                css_path = '#rct-main-app > div.main-app.container-fluid.py-2 > div > div.search-navigation.container.mb-2.d-print-none > div > div.searchbar.row > div.col-12.order-md-2.order-1.col-md-8 > div > div.search-text.col-10.pb-md-0.pb-2.pr-0 > div > div.search-bar-input-container > div > ul > li:nth-child(1) > ul > li:nth-child(1)'
                # css_path = '#rct-main-app > div.main-app.container-fluid.py-2 > div.search-navigation.container.mb-2.d-print-none > div > div.searchbar.row > div.col-12.order-md-2.order-1.col-md-8 > div > div.search-text.col-10.pb-md-0.pb-2.pr-0 > div > div.search-bar-input-container > div > ul > li:nth-child(1) > ul > li:nth-child(1) > a'
                wait = WebDriverWait(driver,2)
                wait.until(EC.text_to_be_present_in_element((By.CSS_SELECTOR, css_path), search_text))
                time.sleep(1)
                suggestion = driver.find_element(By.CSS_SELECTOR, css_path).click()
            except:
                css_path = '#rct-main-app > div.main-app.container-fluid.py-2 > div.search-navigation.container.mb-2.d-print-none > div > div.searchbar.row > div.col-12.order-md-2.order-1.col-md-8 > div > div.search-text.col-10.pb-md-0.pb-2.pr-0 > div > div.search-bar-input-container > div > ul > li:nth-child(1) > ul > li:nth-child(1) > a'
                wait = WebDriverWait(driver, 2)
                wait.until(EC.text_to_be_present_in_element((By.CSS_SELECTOR, css_path), search_text))
                time.sleep(1)
                suggestion = driver.find_element(By.CSS_SELECTOR, css_path).click()
    except TimeoutException:
        time.sleep(1)
        # css_path = '#rct-main-app > div.main-app.container-fluid.py-2 > div > div.search-navigation.container.mb-2.d-print-none > div > div.searchbar.row > div.col-12.order-md-2.order-1.col-md-8 > div > div.search-text.col-10.pb-md-0.pb-2.pr-0 > div > div.search-bar-input-container > div > ul > li:nth-child(2) > ul > li > a > strong'
        suggestion = driver.find_element(By.CSS_SELECTOR, css_path).click()
    except NoSuchElementException:
        submit_button = driver.find_element(By.CLASS_NAME, "btn.btn.submit").click()

def get_property_info(driver):
    wait = WebDriverWait(driver, 10)
    element = wait.until(EC.presence_of_element_located((By.CLASS_NAME, "mailing")))
    owner_info = element.text
    owner_name = get_owner_name(owner_info)
    mailing_addr = get_mailing_address(owner_info)
    return owner_name, mailing_addr

def get_multi_unit(driver, curr_property):
    input_property_info(driver, curr_property)
    time.sleep(2)
    rows = driver.find_element(By.CLASS_NAME, "col-12.results-list.grid")
    # wait = WebDriverWait(driver, 3)
    # rows = wait.until(EC.presence_of_element_located((By.CLASS_NAME, "col-12.results-list.grid")))
    parcels = list()
    parcels.append(re.split(r'\n|Parcel ID', rows.text)[4:][0::6])
    next_page = True
    while next_page:
        try:

            wait = WebDriverWait(driver, 3)
            css_path = '#rct-main-app > div.main-app.container-fluid.py-2 > div > div.search-results.container > div > div.col-12.results-header.mb-2.d-print-none > div > div.col.mt-2.mt-sm-0 > div > ul > li.page-item.next > a'
            # find_next = driver.find_element(By.CSS_SELECTOR, css_path).click()
            find_next = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, css_path)))
            find_next.click()

            time.sleep(1)
            rows = wait.until(EC.presence_of_element_located((By.CLASS_NAME, "col-12.results-list.grid")))
            # rows = driver.find_element(By.CLASS_NAME, "col-12.results-list.grid")
            parcels.append(re.split(r'\n|Parcel ID', rows.text)[4:][0::6])
        except:
            next_page=False
    return parcels



def append_to_df(curr_property, owner_name, mailing_addr, new_df: pd.DataFrame):
    if (curr_property["UNIT_NO"] == " ") | (curr_property.isnull()[6]):
        st_name = f'{curr_property["ST_NAME"]}'
    else:
        st_name = f'{curr_property["ST_NAME"]} {curr_property["UNIT_NO"]}'
    if mailing_addr[0] != "PO":
        new_df.loc[len(new_df)] = [curr_property["ST_NUMB"], st_name, owner_name[1],
                                   owner_name[0],
                                   mailing_addr[0], mailing_addr[1], mailing_addr[2], mailing_addr[3],
                                   mailing_addr[4], ""]
    elif mailing_addr[0] == "PO":
        new_df.loc[len(new_df)] = [curr_property["ST_NUMB"], st_name, owner_name[1],
                                   owner_name[0],
                                   f"{mailing_addr[0]} {mailing_addr[1]}", " ", mailing_addr[2],
                                   mailing_addr[3],
                                   mailing_addr[4], ""]
    elif mailing_addr[0][0] == "#":
        new_df.loc[len(new_df)] = [curr_property["ST_NUMB"], st_name, owner_name[1],
                                   owner_name[0],
                                   mailing_addr[1], mailing_addr[2], mailing_addr[0], mailing_addr[3],
                                   mailing_addr[4], ""]

    return new_df


if __name__ == "__main__":
    df = csv_to_df("../Addresses.csv")