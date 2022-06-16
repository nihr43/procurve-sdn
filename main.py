import logging

from selenium.webdriver import ChromeOptions
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver import Chrome
from selenium.webdriver.chrome.service import Service
from os import environ
from time import sleep
from sys import argv, stderr

log = logging.getLogger(__name__)

def main(argv):
    base = 'http://192.168.2.10/index.html'

    if '--headless' in argv:
        options=headless()
    else:
        options = ChromeOptions()

    s = Service(environ.get('CHROMEDRIVER') or '/usr/bin/chromedriver')
    driver = Chrome(service=s,
                    options=options)


    password=''

    driver.get(base)
    wait = WebDriverWait(driver, 10)
    login(driver, wait, password)
    enable_jumbo_frames(driver, wait)
    enable_lacp(driver, wait)

def headless():
    chrome_options = ChromeOptions()
    # --no-sandbox seems to be necessary in Docker
    # cf https://github.com/joyzoursky/docker-python-chromedriver/blob/master/test_script.py # noqa
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-gpu')
    chrome_options.add_argument('--headless')
    # window size sometimes matters:
    # `Other element would receive the click: <div class="py-3 Footer"></div>`
    chrome_options.add_argument('--window-size=1920,1080')
    return chrome_options


def login(driver, wait, password):
    log.info("Logging in...")
    driver.switch_to.frame("loginFrame")

    wait.until(ec.visibility_of_element_located((By.XPATH, "//input[@id='password']")))
    pass_box = driver.find_element_by_id('password')
#   pass_box.send_keys(password)
    pass_box.send_keys(Keys.RETURN)

    # wait for full page to load before returning
    driver.switch_to.frame("mainFrame")
    wait.until(ec.visibility_of_element_located((By.XPATH, "//*[@name='btnRefresh']")))
    driver.switch_to.default_content()


def enable_jumbo_frames(driver, wait):
    driver.switch_to.frame("loginFrame")
    driver.switch_to.frame("menuFrame")
    ports = wait.until(ec.visibility_of_element_located((By.XPATH, "//*[@id='ports']")))
    ports.click()
    # apparently we have to traverse all the way back down from "default_content" every time we switch frames.
    #   as in, "mainFrame" is not resolvable from "menuFrame".
    driver.switch_to.default_content()
    driver.switch_to.frame("loginFrame")
    driver.switch_to.frame("mainFrame")
    jumbo_checkbox = wait.until(ec.visibility_of_element_located((By.XPATH, "//input[@id='R10']")))
    if not jumbo_checkbox.is_selected():
        jumbo_checkbox.click()
        apply = driver.find_element_by_name('btnSaveSettings')
        apply.click()
    driver.switch_to.default_content()


def enable_lacp(driver, wait):
    driver.switch_to.frame("loginFrame")
    driver.switch_to.frame("menuFrame")
    trunks = wait.until(ec.visibility_of_element_located((By.XPATH, "//*[@id='trunks']")))
    trunks.click()
    lacp_setup = wait.until(ec.visibility_of_element_located((By.XPATH, "//*[@id='trunksla']")))
    lacp_setup.click()
    driver.switch_to.default_content()
    driver.switch_to.frame("loginFrame")
    driver.switch_to.frame("mainFrame")

    lacp_checkboxes = driver.find_elements_by_xpath("//input[@type='checkbox']")

    boxes_mutated = []

    for check in lacp_checkboxes:
        if not check.is_selected():
            check.click()
            boxes_mutated.append(check)

    if boxes_mutated:
        apply = driver.find_element_by_name('btnSaveSettings')
        apply.click()
        alert = driver.switch_to.alert
        alert.accept()

    driver.switch_to.default_content()


if __name__ == '__main__':
    main(argv[:])
