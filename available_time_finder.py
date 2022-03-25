from time import sleep
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup
from collections import defaultdict


def init_driver():
    options = Options()
    options.add_argument("start-maximized")
    options.add_experimental_option('excludeSwitches', ['enable-logging'])
    return webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)


def navigate_to_times_page(url, driver):
    driver.get(url)
    driver.find_element(by=By.NAME, value="StartNextButton").click()
    driver.find_element(by=By.NAME, value="AcceptInformationStorage").click()
    driver.find_element(by=By.NAME, value="Next").click()
    driver.find_element(by=By.ID, value="ServiceCategoryCustomers_0__ServiceCategoryId").click()
    driver.find_element(by=By.NAME, value="Next").click()


def get_available_times_source(driver):
    driver.find_element(by=By.NAME, value="TimeSearchFirstAvailableButton").click()
    return driver.page_source


def get_available_times(cell):
    result = defaultdict(list)
    soup = BeautifulSoup(page_source, 'html.parser')
    cells = soup.find_all('td', {"class":"timetable-cells"})
    if cells:
        for cell in cells:
            city = cell['headers'][0]
            time = cell.find_all('input', {"name":"ReservedDateTime"})[0]['value']
            result[city].append(time)
    return result


if __name__ == '__main__':
    driver = init_driver()
    url = 'https://bokapass.nemoq.se/Booking/Booking/Index/skane'
    navigate_to_times_page(url, driver)
    while True:
        page_source = get_available_times_source(driver)
        available_times = get_available_times(page_source)
        for city, times in available_times.items():
            print(city)
            print(times)
            print()
        sleep(10)
