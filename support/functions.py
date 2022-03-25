import time

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys


GLOBAL_SLEEP = 3


def close_other_tabs(input_driver):
    # Get current window handle
    current_window = input_driver.current_window_handle
    # Get first child window
    all_windows = input_driver.window_handles
    for window in all_windows:
        # switch focus to child window
        if window != current_window:
            input_driver.switch_to.window(window)
            input_driver.close()
    input_driver.switch_to.window(current_window)


def check_element(input_driver, input_xpath):
    time.sleep(GLOBAL_SLEEP)
    elem_list = input_driver.find_elements(By.XPATH, input_xpath)
    elem_number = len(elem_list)
    if elem_number == 1:
        return True
    elif elem_number > 1:
        raise Exception('Too many elements found')
    else:
        raise Exception('The element not found')


def click_element(input_driver, input_xpath):
    try:
        time.sleep(GLOBAL_SLEEP)
        ui_element = input_driver.find_element(By.XPATH, input_xpath)
        ui_element.click()
    except Exception as click_error:
        print(click_error.args)
        pass


def sendkeys_element(input_driver, input_xpath, input_value):
    try:
        time.sleep(GLOBAL_SLEEP)
        ui_element = input_driver.find_element(By.XPATH, input_xpath)
        ui_element.send_keys(input_value)
    except Exception as click_error:
        print(click_error.args)
        pass
