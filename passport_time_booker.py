from time import sleep
from datetime import datetime
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


def get_available_times(page_source):
    result = defaultdict(list)
    soup = BeautifulSoup(page_source, 'html.parser')
    day_text_span = soup.find('span', {"id":"dayText"})
    day_text = ''
    if day_text_span:
        day_text = day_text_span.string.split()[0]
    cells = soup.find_all('td', {"class":"timetable-cells"})
    if cells:
        for cell in cells:
            city = cell['headers'][0]
            date = cell.find_all('input', {"name":"ReservedDateTime"})[0]['value']
            result[city].append(date)
    return day_text, result


def get_accepted_date(day_text, available_times, conditions):
    current_date = datetime.now()
    if day_text in conditions['accepted_days']:
        for city in conditions['accepted_cities']:
            dates = available_times[city]
            for date_str in dates:
                date = datetime.strptime(date_str, '%Y-%m-%d %H:%M:%S')
                duration = date - current_date
                offset = duration.total_seconds()/3600
                if date.hour >= conditions['earliest_accepted_hour'] and offset >= conditions['hours_offset']:
                    print(city, date)
                    return date
    return None


def book_passport_time(url, conditions):
    driver = init_driver()
    navigate_to_times_page(url, driver)

    accepted_date = None
    while not accepted_date:
        page_source = get_available_times_source(driver)
        day_text, available_times = get_available_times(page_source)
        accepted_date = get_accepted_date(day_text, available_times, conditions)
        if accepted_date:
            break
        sleep(10)

    driver.find_element(by=By.CSS_SELECTOR, value=f"[aria-label=\'{accepted_date}\']").click()
    driver.find_element(by=By.NAME, value="Next").click()
    input()


if __name__ == '__main__':
    url = 'https://bokapass.nemoq.se/Booking/Booking/Index/skane'
    conditions = {
        'accepted_days': ['lördag', 'tisdag', 'måndag', 'onsdag'],
        'accepted_cities': ['Malmö', 'Lund', 'Hässleholm'],
        'earliest_accepted_hour': 11,
        'hours_offset': 48
    }
    book_passport_time(url, conditions)
