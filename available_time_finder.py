from selenium import webdriver
from selenium.webdriver.support.ui import Select
import requests
from bs4 import BeautifulSoup
import sys, os
import re

class Available_time_finder:
    def __init__(self, url, area, number_results):
        self.url = url
        self.area = area
        self.number_results = number_results
        print("Loading browser driver...")
        self.load_driver("firefox")
        self.connect_to(self.url)
        self.get_results()
        self.close_driver()

    def load_driver(self, browser):
        _platform = sys.platform
        if _platform == "linux" or _platform == "linux2": # linux
            firefox_driver_path = os.path.join('drivers', 'geckodriver_linux')
            chrome_driver_path = os.path.join('drivers', 'chromedriver_linux')
        elif _platform == "darwin": # MAC OS X
            firefox_driver_path = os.path.join('drivers', 'geckodriver_mac')
            chrome_driver_path = os.path.join('drivers', 'chromedriver_mac')
        elif _platform == "win32" or _platform == "win64": # Windows
            firefox_driver_path = os.path.join('drivers', 'geckodriver_win')
            chrome_driver_path = os.path.join('drivers', 'chromedriver_win')

        if browser == 'firefox':
            try:
                from selenium.webdriver.firefox.options import Options
                firefox_options = Options()
                firefox_options.add_argument("--headless")
                self.driver = webdriver.Firefox(executable_path=firefox_driver_path, firefox_options=firefox_options)
                print("Loaded firefox driver.")
            except Exception as e:
                if 'executable needs to be in PATH' in str(e): #driver not found
                    msg = "Firefox webdriver is missing! Try reinstalling the program."
                    print(msg)
                    sys.exit(1)
                else:
                    self.load_driver('chrome')
        elif browser == 'chrome':
            try:
                from selenium.webdriver.chrome.options import Options
                chrome_options = Options()
                chrome_options.add_argument("--headless")
                self.driver = webdriver.Chrome(executable_path=chrome_driver_path, chrome_options=chrome_options)
                print("Loaded chrome driver.")
            except Exception as e:
                print(e)
                if 'executable needs to be in PATH' in str(e): #driver not found
                    msg = "Chrome webdriver is missing! Try reinstalling the program."
                    print(msg)
                    sys.exit(1)
                else:
                    self.load_driver(None)
        else:
            msg = "To use extensive run either Firefox or Chrome browser should be installed!"
            print(msg)
            sys.exit(1)

    def connect_to(self, url):
        print("Connecting...")
        self.driver.get(url)
        self.driver.find_element_by_name("NextButtonID20").click()
        self.driver.find_element_by_name("AcceptInformationStorage").click()
        self.driver.find_element_by_xpath("//div[@class='btn-toolbar']//input[@name='Next']").click()
        options = Select(self.driver.find_element_by_id('SectionId'))
        options.select_by_visible_text(self.area)
        print("Found source.")

    def get_results(self):
        self.driver.find_element_by_name("TimeSearchFirstAvailableButton").click()
        self.page_source = self.driver.page_source
        self.soup = BeautifulSoup(self.page_source, 'html.parser')
        cells = self.soup.find_all('div', {"data-function":"timeTableCell"})
        available_times = []
        for cell in cells:
            if cell["aria-label"] != "Bokad":
                available_times.append(cell["aria-label"])
        def getKey(item):
            return re.findall(r'\b\d+\b', item)
        available_times = sorted(available_times, key=getKey)
        for i in range(self.number_results):
            if i < len(available_times):
                print(available_times[i])

    def close_driver(self):
        self.driver.stop_client()
        self.driver.close()
        self.driver.quit()

if __name__ == '__main__':
    url = "https://ventus.enalog.se/Booking/Booking/Index/skane"
    area = "Lund"
    number_results = 10
    Available_time_finder(url, area, number_results)

