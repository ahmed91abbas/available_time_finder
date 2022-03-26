import json
from time import sleep
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup
from collections import defaultdict


class PassportTimeBooker:
    def __init__(self, url, config_file_path, confirmations_file_path):
        self.url = url
        self.confirmations_file_path = confirmations_file_path
        self.config = self.get_config(config_file_path)

    def get_config(self, config_file_path):
        with open(config_file_path, 'r') as f:
            return json.loads(f.read())

    def book_passport_time(self):
        self.init_driver()
        self.navigate_to_times_page()
        accepted_date = None
        while not accepted_date:
            page_source = self.get_available_times_source()
            day_text, available_times = self.get_available_times(page_source)
            accepted_date = self.get_accepted_date(day_text, available_times)
            if accepted_date:
                break
            sleep(10)
        self.confirm_booking(accepted_date)
        self.write_confirmation_to_file()

    def init_driver(self):
        options = Options()
        options.add_argument("start-maximized")
        options.add_experimental_option('excludeSwitches', ['enable-logging'])
        self.driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

    def navigate_to_times_page(self):
        self.driver.get(self.url)
        # page: Välkommen till tidsbokningen i Skåne län
        self.driver.find_element(by=By.NAME, value="StartNextButton").click()
        # page: Behandling av personuppgifter
        self.driver.find_element(by=By.NAME, value="AcceptInformationStorage").click()
        self.driver.find_element(by=By.NAME, value="Next").click()
        # page: Bor du i Sverige?
        self.driver.find_element(by=By.ID, value="ServiceCategoryCustomers_0__ServiceCategoryId").click()
        self.driver.find_element(by=By.NAME, value="Next").click()

    def get_available_times_source(self):
        # page: Välj tid
        self.driver.find_element(by=By.NAME, value="TimeSearchFirstAvailableButton").click()
        return self.driver.page_source

    def get_available_times(self, page_source):
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

    def get_accepted_date(self, day_text, available_times):
        current_date = datetime.now()
        if day_text in self.config['conditions']['accepted_days']:
            for city in self.config['conditions']['accepted_cities']:
                dates = available_times[city]
                for date_str in dates:
                    date = datetime.strptime(date_str, '%Y-%m-%d %H:%M:%S')
                    duration = date - current_date
                    offset = duration.total_seconds()/3600
                    is_accepted_hour = date.hour >= self.config['conditions']['earliest_accepted_hour']
                    is_accepted_offset = offset >= self.config['conditions']['hours_offset']
                    if is_accepted_hour and is_accepted_offset:
                        print(city, date)
                        return date
        return None

    def confirm_booking(self, date):
        # page: Välj tid
        self.driver.find_element(by=By.CSS_SELECTOR, value=f"[aria-label=\'{date}\']").click()
        self.driver.find_element(by=By.NAME, value="Next").click()
        # page: Uppgifter till bokningen
        self.driver.find_element(by=By.ID, value="Customers_0__BookingFieldValues_0__Value").send_keys(self.config['first_name'])
        self.driver.find_element(by=By.ID, value="Customers_0__BookingFieldValues_1__Value").send_keys(self.config['last_name'])
        self.driver.find_element(by=By.ID, value="Customers_0__Services_0__IsSelected").click()
        self.driver.find_element(by=By.NAME, value="Next").click()
        # page: Viktig information
        self.driver.find_element(by=By.NAME, value="Next").click()
        # page: Kontaktuppgifter
        self.driver.find_element(by=By.ID, value="EmailAddress").send_keys(self.config['email'])
        self.driver.find_element(by=By.ID, value="ConfirmEmailAddress").send_keys(self.config['email'])
        self.driver.find_element(by=By.ID, value="SelectedContacts_0__IsSelected").click()
        self.driver.find_element(by=By.ID, value="SelectedContacts_2__IsSelected").click()
        self.driver.find_element(by=By.NAME, value="Next").click()
        # page: Bekräfta bokning
        self.driver.find_element(by=By.NAME, value="Next").click()

    def write_confirmation_to_file(self):
        page_source = self.driver.page_source
        soup = BeautifulSoup(page_source, 'html.parser')
        labels = soup.find_all('label', {'class':'control-label'})
        values = soup.find_all('b', {'class':'control-freetext'}) + soup.find_all('span', {'class':'control-freetext'})
        pairs = list(zip(labels, values))
        details = [f'{label.string} {value.string}' for label, value in pairs if value.string is not None]
        details.append(f'Namn: {self.config["first_name"]} {self.config["last_name"]}')
        details.append(f'Email: {self.config["email"]}')
        details = '\n'.join(details)
        with open(self.confirmations_file_path, 'a+', encoding='utf-8') as f:
            seperator = '*'*60
            f.write(details)
            f.write(f'\n\n{seperator}\n\n')


if __name__ == '__main__':
    url = 'https://bokapass.nemoq.se/Booking/Booking/Index/skane'
    config_file_path = 'config.json'
    confirmations_file_path = 'confirmations.txt'
    booker = PassportTimeBooker(url, config_file_path, confirmations_file_path)
    booker.book_passport_time()
    input()
