import logging

from selenium.webdriver import ChromeOptions
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver import Chrome
from selenium.webdriver.chrome.service import Service
from os import environ
from sys import argv

log = logging.getLogger(__name__)


def main(argv):
    base = 'http://192.168.2.10/index.html'

    if '--headless' in argv:
        options = headless()
    else:
        options = ChromeOptions()

    s = Service(environ.get('CHROMEDRIVER') or '/usr/bin/chromedriver')
    driver = Chrome(service=s,
                    options=options)

    password = ''

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


# it appears we have to traverse all the way down from default_content whenever we switch frames
def to_menu(driver):
    driver.switch_to.default_content()
    driver.switch_to.frame("loginFrame")
    driver.switch_to.frame("menuFrame")


def to_main(driver):
    driver.switch_to.default_content()
    driver.switch_to.frame("loginFrame")
    driver.switch_to.frame("mainFrame")


def login(driver, wait, password):
    log.info("Logging in...")
    driver.switch_to.frame("loginFrame")

    pass_box = wait.until(ec.visibility_of_element_located((By.XPATH, "//input[@id='password']")))
#   pass_box.send_keys(password)
    pass_box.send_keys(Keys.RETURN)

    # wait for full page to load before returning
    to_main(driver)
    wait.until(ec.visibility_of_element_located((By.XPATH, "//*[@name='btnRefresh']")))


def enable_jumbo_frames(driver, wait):
    to_menu(driver)
    ports = wait.until(ec.visibility_of_element_located((By.XPATH, "//*[@id='ports']")))
    ports.click()
    to_main(driver)
    jumbo_checkbox = wait.until(ec.visibility_of_element_located((By.XPATH, "//input[@id='R10']")))
    if not jumbo_checkbox.is_selected():
        jumbo_checkbox.click()
        apply = driver.find_element_by_name('btnSaveSettings')
        apply.click()


def enable_lacp(driver, wait):
    to_menu(driver)
    trunks = wait.until(ec.visibility_of_element_located((By.XPATH, "//*[@id='trunks']")))
    trunks.click()

    lacp_setup = wait.until(ec.visibility_of_element_located((By.XPATH, "//*[@id='trunksla']")))
    lacp_setup.click()
    to_main(driver)
    lacp_checkboxes = driver.find_elements(by=By.XPATH, value="//input[@type='checkbox']")

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


if __name__ == '__main__':
    main(argv[:])
