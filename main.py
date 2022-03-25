from support import functions as f
from support import ui_elements as ui

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys

import glob
import os
import csv
import json
import requests
import time


# Load config parameters
with open('config.json') as config:
    CONFIG = json.load(config)

# Create url to get all profiles, get all profiles
list_url = '{}:{}/api/v1/user/list?page_size={}'.format(CONFIG['ADSPOWER_URL'],
                                                        CONFIG['ADSPOWER_PORT'],
                                                        CONFIG['PAGE_SIZE'],)
resp_list = requests.get(list_url).json()
# Get profiles which already done
list_of_files = os.listdir(CONFIG['FOLDER_FOR_KEYS'])
list_of_names = [filename.split('.')[0] for filename in list_of_files]

# ---------------------------------------------------------------------------------------
# Start processing each profile
for profile in resp_list['data']['list']:

    # Check if the profile has been processed before
    if profile['user_id'] in list_of_names:
        print('{} already processed'.format(profile['user_id']))
        continue

    # TODO: add empty response and exception handling
    # TODO: add exception handling (logs)
    CURRENT_RECORD = []

    open_url = '{}:{}/api/v1/browser/start?user_id={}'.format(CONFIG['ADSPOWER_URL'],
                                                              CONFIG['ADSPOWER_PORT'],
                                                              profile['user_id'])

    close_url = '{}:{}/api/v1/browser/stop?user_id={}'.format(CONFIG['ADSPOWER_URL'],
                                                              CONFIG['ADSPOWER_PORT'],
                                                              profile['user_id'])

    resp = requests.get(open_url).json()
    CURRENT_RECORD.append(profile['user_id'])

    # Set up selenium
    chrome_driver = resp["data"]["webdriver"]
    chrome_options = Options()
    chrome_options.add_experimental_option("debuggerAddress", resp["data"]["ws"]["selenium"])
    driver = webdriver.Chrome(chrome_driver, options=chrome_options)

    # ---------------------------------------------------------------------------------------
    # Set up Metamask
    # 0 - Create wallet
    # 1 - Login
    driver.get(CONFIG['METAMASK_URL'])
    # Close other tabs
    f.close_other_tabs(driver)
    # Try to create wallet
    driver.get(CONFIG['METAMASK_URL'])

    try:
        flow_flag = f.check_element(driver, ui.xpath_getstarted)

        if flow_flag:
            # GetStarted element already defined
            f.click_element(driver, ui.xpath_getstarted)

            # Click Create button
            f.click_element(driver, ui.xpath_create1)

            # Click No, thanks button
            f.click_element(driver, ui.xpath_nothanks)

            # Enter a new password
            f.sendkeys_element(driver, ui.xpath_newpass, CONFIG['DEFAULT_PASS'])

            # Enter a new password once again (confirm)
            f.sendkeys_element(driver, ui.xpath_confirmpass, CONFIG['DEFAULT_PASS'])

            # Click checkbox I have read terms
            f.click_element(driver, ui.xpath_ihaveread)

            # Click Create button
            f.click_element(driver, ui.xpath_create2)

            # Click Next button
            f.click_element(driver, ui.xpath_mmnext)

            # Download secret key (seed)
            f.click_element(driver, ui.xpath_download)

            # Click Remind me later (do not reveal seed)
            f.click_element(driver, ui.xpath_later)

            # Rename a downloaded file (wit seed)
            search_pattern = CONFIG['DOWNLOADS_FOLDER'] + '/*.txt'
            list_of_files = glob.glob(search_pattern)
            latest_file = max(list_of_files, key=os.path.getctime)
            # Absolute path to the file
            new_name = CONFIG['FOLDER_FOR_KEYS'] + '/' + profile['user_id'] + '.txt'
            os.rename(latest_file, new_name)

    except Exception as err:
        print(err.args)
        time.sleep(CONFIG['GLOBAL_SLEEP'])
        pass

    # Login (if required)
    try:
        flow_flag = f.check_element(driver, ui.xpath_password)

        if flow_flag:
            f.sendkeys_element(driver, ui.xpath_password, CONFIG['DEFAULT_PASS'])
            f.sendkeys_element(driver, ui.xpath_password, Keys.RETURN)

    except Exception as err:
        print(err.args)
        time.sleep(CONFIG['GLOBAL_SLEEP'])
        pass

    # Launch DEX (Refer & Earn section)
    driver.maximize_window()
    driver.get(CONFIG['DEX_URL'])

    # ---------------------------------------------------------------------------------------
    # Connect wallet (if not connected) and select Metamask
    try:
        flow_flag = f.check_element(driver, ui.xpath_connect)

        if flow_flag:
            f.click_element(driver, ui.xpath_connect)

            # Select Metamask
            flow_flag = f.check_element(driver, ui.xpath_mmbutton)
            f.click_element(driver, ui.xpath_mmbutton) if flow_flag else None

    except Exception as err:
        print(err.args)
        time.sleep(CONFIG['GLOBAL_SLEEP'])
        pass

    # ---------------------------------------------------------------------------------------
    # Switch to Polygon (if not already switched)
    try:
        flow_flag = f.check_element(driver, ui.xpath_switch)

        if flow_flag:
            f.click_element(driver, ui.xpath_switch)

            # Go to metamask html page (we can't work with Metamask unless we open its popup as a new tab)
            driver.get(CONFIG['METAMASK_URL'])

            # Approve adding a network (this popup appears if Polygon not saved in Metamask)
            # (press Approve button)
            flow_flag = f.check_element(driver, ui.xpath_approve)
            f.click_element(driver, ui.xpath_approve) if flow_flag else None

            # Switch to Polygon (press Switch network button)
            f.click_element(driver, ui.xpath_switchmm)

    except Exception as err:
        print(err.args)
        time.sleep(CONFIG['GLOBAL_SLEEP'])
        pass

    # ---------------------------------------------------------------------------------------
    # Go back to Polysynth and enter a referral code
    # TODO: replace with smart wait
    driver.get(CONFIG['DEX_URL'])

    # Connect wallet (if not connected) and select Metamask
    try:
        flow_flag = f.check_element(driver, ui.xpath_connect)

        if flow_flag:
            # Click Connect button
            f.click_element(driver, ui.xpath_connect)

            # Select Metamask in pop-up
            flow_flag = f.check_element(driver, ui.xpath_mmbutton)
            f.click_element(driver, ui.xpath_mmbutton) if flow_flag else None

            # Select account
            driver.get(CONFIG['METAMASK_URL'])

            flow_flag = f.check_element(driver, ui.xpath_nextbutton)

            if flow_flag:
                # Click Next button (approve connection to accounts picked by default)
                f.click_element(driver, ui.xpath_nextbutton)

                # Click Connect
                f.click_element(driver, ui.xpath_mmconnect)

    except Exception as err:
        print(err.args)
        time.sleep(CONFIG['GLOBAL_SLEEP'])
        pass

    # Click the link
    driver.get(CONFIG['DEX_URL'])

    f.click_element(driver, ui.xpath_reflink)

    # Enter the referral code
    f.sendkeys_element(driver, ui.xpath_refcode, CONFIG['REF_CODE'])

    # Submit
    # TODO: save a screenshot
    flow_flag = f.check_element(driver, ui.xpath_submit)
    f.click_element(driver, ui.xpath_submit) if flow_flag else None

    # TODO: check entered value and errors
    elem_yourrefcode = driver.find_element(By.XPATH, ui.xpath_yourrefcode)
    # Save public address
    CURRENT_RECORD.append(elem_yourrefcode.text)

    # Done! Quit and go to the next one
    driver.quit()
    requests.get(close_url)

    with open('processed_profiles.csv', 'a', newline="") as file:
        writer = csv.writer(file)
        writer.writerow(CURRENT_RECORD)
