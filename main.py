import requests
import time
import functions as f

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys

import glob
import os
import csv
import json

with open('config.json') as config:
    CONFIG = json.load(config)

list_url = '{}:{}/api/v1/user/list?page_size={}'.format(CONFIG['ADSPOWER_URL'],
                                                        CONFIG['ADSPOWER_PORT'],
                                                        CONFIG['PAGE_SIZE'],)

# Get all profiles stored in AdsPower
resp_list = requests.get(list_url).json()
# Get profiles which already done
list_of_files = os.listdir(CONFIG['FOLDER_FOR_KEYS'])
list_of_names = [filename.split('.')[0] for filename in list_of_files]

for profile in resp_list['data']['list']:

    # Check if the profile has been processed before
    # if profile['user_id'] in list_of_names:
    #    print('{} already processed'.format(profile['user_id']))
    #    continue

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
        xpath_getstarted = '//*[@id="app-content"]/div/div[2]/div/div/div/button'
        flow_flag = f.check_element(driver, xpath_getstarted)

        if flow_flag:
            # GetStarted element already defined
            f.click_element(driver, xpath_getstarted)

            # Click Create button
            xpath_create1 = '//*[@id="app-content"]/div/div[2]/div/div/div[2]/div/div[2]/div[2]/button'
            f.click_element(driver, xpath_create1)

            # Click No, thanks button
            xpath_nothanks = '//*[@id="app-content"]/div/div[2]/div/div/div/div[5]/div[1]/footer/button[1]'
            f.click_element(driver, xpath_nothanks)

            # Enter a new password
            xpath_newpass = '//*[@id="create-password"]'
            f.sendkeys_element(driver, xpath_newpass, CONFIG['DEFAULT_PASS'])

            # Enter a new password once again (confirm)
            xpath_confirmpass = '//*[@id="confirm-password"]'
            f.sendkeys_element(driver, xpath_confirmpass, CONFIG['DEFAULT_PASS'])

            # Click checkbox I have read terms
            xpath_ihaveread = '//*[@id="app-content"]/div/div[2]/div/div/div[2]/form/div[3]/div'
            f.click_element(xpath_ihaveread)

            # Click Create button
            xpath_create2 = '//*[@id="app-content"]/div/div[2]/div/div/div[2]/form/button'
            f.click_element(driver, xpath_create2)

            # Click Next button
            xpath_mmnext = '//*[@id="app-content"]/div/div[2]/div/div/div[2]/div/div[1]/div[2]/button'
            f.click_element(driver, xpath_mmnext)

            # Download secret key (seed)
            xpath_download = '//*[@id="app-content"]/div/div[2]/div/div/div[2]/div[1]/div[2]/div[5]/a'
            f.click_element(driver, xpath_download)

            # Click Remind me later (do not reveal seed)
            xpath_later = '//*[@id="app-content"]/div/div[2]/div/div/div[2]/div[2]/button[1]'
            f.click_element(driver, xpath_later)

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
        xpath_password = '//*[@id="password"]'
        flow_flag = f.check_element(driver, xpath_password)

        if flow_flag:
            f.sendkeys_element(driver, xpath_password, CONFIG['DEFAULT_PASS'])
            f.sendkeys_element(driver, xpath_password, Keys.RETURN)

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
        xpath_connect = '//*[@id="__next"]/div/div[1]/div/div[1]/div[2]/div[2]/div[3]/div/p[1]'
        flow_flag = f.check_element(driver, xpath_connect)

        if flow_flag:
            f.click_element(driver, xpath_connect)

            # Select Metamask
            xpath_mmbutton = '/html/body/div[4]/div/div/div/div[2]/div/div[1]/div[2]/h4'
            flow_flag = f.check_element(driver, xpath_mmbutton)
            f.click_element(driver, xpath_mmbutton) if flow_flag else None

    except Exception as err:
        print(err.args)
        time.sleep(CONFIG['GLOBAL_SLEEP'])
        pass

    # ---------------------------------------------------------------------------------------
    # Switch to Polygon (if not already switched)
    try:
        xpath_switch = '//*[@id="__next"]/div/div[1]/div/div[1]/div[2]/div[2]/div[3]/div/p'
        flow_flag = f.check_element(driver, xpath_switch)

        if flow_flag:
            f.click_element(driver, xpath_switch)

            # Go to metamask html page (we can't work with Metamask unless we open its popup as a new tab)
            driver.get(CONFIG['METAMASK_URL'])

            # Approve adding a network (this popup appears if Polygon not saved in Metamask)
            # (press Approve button)
            xpath_approve = '//*[@id="app-content"]/div/div[2]/div/div[2]/div/button[2]'
            flow_flag = f.check_element(driver, xpath_approve)
            f.click_element(driver, xpath_approve) if flow_flag else None

            # Switch to Polygon (press Switch network button)
            xpath_switchmm = '//*[@id="app-content"]/div/div[2]/div/div[2]/div[2]/button[2]'
            f.click_element(driver, xpath_switchmm)

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
        xpath_connect = '//*[@id="__next"]/div/div[1]/div/div[1]/div[2]/div[2]/div[3]/div/p[1]'
        flow_flag = f.check_element(driver, xpath_connect)

        if flow_flag:
            # Click Connect button
            f.click_element(driver, xpath_connect)

            # Select Metamask in pop-up
            xpath_mmbutton = '/html/body/div[4]/div/div/div/div[2]/div/div[1]/div[2]/h4'
            flow_flag = f.check_element(driver, xpath_mmbutton)
            f.click_element(driver, xpath_mmbutton) if flow_flag else None

            # Select account
            driver.get(CONFIG['METAMASK_URL'])

            xpath_nextbutton = '//*[@id="app-content"]/div/div[2]/div/div[2]/div[3]/div[2]/button[2]'
            flow_flag = f.check_element(driver, xpath_nextbutton)

            if flow_flag:
                # Click Next button (approve connection to accounts picked by default)
                f.click_element(driver, xpath_nextbutton)

                # Click Connect
                xpath_mmconnect = '//*[@id="app-content"]/div/div[2]/div/div[2]/div[2]/div[2]/footer/button[2]'
                f.click_element(driver, xpath_mmconnect)

    except Exception as err:
        print(err.args)
        time.sleep(CONFIG['GLOBAL_SLEEP'])
        pass

    # Click the link
    driver.get(CONFIG['DEX_URL'])

    xpath_reflink = '//*[@id="__next"]/div/div[1]/div/div[3]/div/div[1]/div/div/div/div[1]/div[4]/p'
    f.click_element(driver, xpath_reflink)

    # Enter the referral code
    xpath_refcode = '/html/body/div[8]/div/div/div/div/div[2]/input'
    f.sendkeys_element(driver, xpath_refcode, CONFIG['REF_CODE'])

    # Submit
    # TODO: save a screenshot
    xpath_submit = '/html/body/div[8]/div/div/div/div/div[2]/div/button'
    flow_flag = f.check_element(driver, xpath_submit)
    f.click_element(driver, xpath_submit) if flow_flag else None

    # TODO: check entered value and errors
    xpath_yourrefcode = '//*[@id="__next"]/div/div[1]/div/div[3]/div/div[1]/div/div/div/div[1]/div[2]/div/h6'
    elem_yourrefcode = driver.find_element(By.XPATH, xpath_yourrefcode)
    # Save public address
    CURRENT_RECORD.append(elem_yourrefcode.text)

    # Done! Quit and go to the next one
    driver.quit()
    requests.get(close_url)

    with open('processed_profiles.csv', 'a', newline="") as file:
        writer = csv.writer(file)
        writer.writerow(CURRENT_RECORD)
