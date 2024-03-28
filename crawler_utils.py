import imp
import re
import sys, json
from time import sleep
import time
from bs4 import BeautifulSoup
from parsel import Selector
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys

class Crawler:
    def __init__(self,  linkedin_username=None , linkedin_password=None):
        self.linkedin_username = linkedin_username
        self.linkedin_password = linkedin_password

    def load_chrome_web_driver(self, path):
        service = webdriver.ChromeService(executable_path = path)
        driver = webdriver.Chrome(service=service)
        return driver

    def phantom_buster(self, path):
        driver = webdriver.PhantomJS(executable_path=path)
        return driver

    def find_element_by_id_name(self, id, value, driver, sleep_time =1.5):
        field_value = driver.find_element(By.ID, id)
        field_value.send_keys(value)
        sleep(sleep_time)

    def login(self, driver, sleep_time):
        self.find_element_by_id_name(id = 'username', value = self.linkedin_username , driver= driver)
        self.find_element_by_id_name(id = 'password', value = self.linkedin_password , driver =  driver)
        self.button_click(driver)

    def search_keyword(self, driver, keyword):
        try:
            search = driver.find_element(By.CLASS_NAME,"search-global-typeahead__collapsed-search-button-icon" )
            search.click()        
        except:
            pass
      
        input_field = driver.find_element(By.CLASS_NAME, "search-global-typeahead__input")
        input_field.send_keys(keyword)
        input_field.send_keys(Keys.RETURN)

    def search_people(self, driver):
        xpath = "//li[contains(@class, 'search-reusables__primary-filter') and contains(., 'People')]"
        people = driver.find_element(By.XPATH, xpath)
        people.click()

    def next(self, driver, text = "Next"):
        initialScroll = 0
        finalScroll = 1000
        driver.execute_script(f"window.scrollTo({initialScroll}, {finalScroll})")
        time.sleep(3)
        xpath = f"//span[contains(@class, 'artdeco-button__text') and contains(., '{text}')]"
        next_button = driver.find_element(By.XPATH, xpath)
        next_button.click()

    def get_list_cv(self, driver):
        lst_candidates = []
        xpath = "//div[@class='entity-result__universal-image']//a[@class='app-aware-link  scale-down ']"
        a_elements = driver.find_elements(By.XPATH, xpath)

        for a_element in a_elements:
            href_value = a_element.get_attribute("href")
            print(href_value)
            lst_candidates.append(href_value)
        return lst_candidates

    def get_list_candidates(self, driver, keyword, max_value=1000000):
        self.find_element_by_id_name('username', self.linkedin_username , driver)
        self.find_element_by_id_name('password', self.linkedin_password , driver)
        self.button_click(driver)
        sleep(2)
        self.search_keyword(driver, keyword)
        sleep(5)
        self.search_people(driver)
        lst_candidates = []
        step = 0
        while step < max_value:
            try: 
                lst_candidates.extend(self.get_list_cv(driver))
                sleep(3)
                self.next(driver, "Next")
                sleep(3)
            except Exception as e:
                print(f"Error occurred: {e}")
                break
            step += 1
        return lst_candidates
        

    def button_click(self, driver):
        button = driver.find_element(By.CSS_SELECTOR, "button.btn__primary--large.from__button--floating")
        button.click()
        sleep(1.5)

    def collect_name(self, selector):
        name = selector.xpath('//*[starts-with(@class, "inline t-24 t-black t-normal break-words")]/text()').extract_first()
        return name

    def collect_companies(self,selector):
        companies = selector.xpath('//*[starts-with(@class, "pv-entity__secondary-title t-14 t-black t-normal")]/text()').getall()
        return companies

    def collect_designations(self, selector):
        designations = selector.xpath('//li//div//div//a//div//h3[starts-with(@class, "t-16 t-black t-bold")]/text()').getall()
        return designations

    def collect_companies_start_end_date(self, selector):
            
        dates = selector.xpath('//li//div//div//a//div//div//h4[starts-with(@class, "pv-entity__date-range t-14 t-black--light t-normal")]//span/text()').getall()
        dates = [date for date in dates if date != 'Dates Employed']
        dates = [re.sub('–', '-', date) for date in dates]
        return dates

    def collect_location(self, selector):
        location = selector.xpath('//*[starts-with(@class, "t-16 t-black t-normal inline-block")]/text()').extract_first()
        return location
            

    def collect_university(self, selector):
        universities = selector.xpath('//*[starts-with(@class, "pv-entity__school-name t-16 t-black t-bold")]/text()').getall()
        return universities

    def collect_studies(self, selector):
        studies = selector.xpath('//*[starts-with(@class, "pv-entity__comma-item")]/text()').getall()
        return studies
        
    def collect_universities_studies_time(self, selector):
        time = selector.xpath('//*[starts-with(@class, "pv-entity__dates t-14 t-black--light t-normal")]//span//time/text()').getall()
        return time
    
    def get_info(self, driver, link_candidates):
        driver.get(link_candidates)
        start = time.time()
        initialScroll = 0
        finalScroll = 1000
        while True:
            driver.execute_script(f"window.scrollTo({initialScroll}, {finalScroll})")
            initialScroll = finalScroll
            finalScroll += 1000
            time.sleep(3)
            end = time.time()
            if round(end - start) > 15:
                break
        page_source = driver.page_source
        soup = BeautifulSoup(page_source, 'html.parser')
        intro = soup.find('div', {'class': 'mt2 relative'})
        name_loc = intro.find('h1')
        name = name_loc.text.strip()

        company_loc = soup.find('ul', class_='pv-text-details__right-panel')
        company = company_loc.find_all('button', attrs={"aria-label": lambda x: x and "Current company" in x})[0].find('span').text.strip()


        location_loc = intro.find_all('span', {'class': 'text-body-small inline t-black--light break-words'})
        location = location_loc[0].text.strip()

        education_section = soup.find(lambda tag: tag.name == 'section' and tag.find('div', {'id': 'education'}))
        education_school = [
            span_element.text.strip()
            for div_element in education_section.find_all('div', class_='display-flex align-items-center mr1 hoverable-link-text t-bold')
            for span_element in div_element.find_all('span', attrs={"aria-hidden": "true"})
        ]
        education_time = [
            span_element.text.strip()
            for div_element in education_section.find_all('span', class_ = 't-14 t-normal t-black--light')
            for span_element in div_element.find_all('span', attrs={"aria-hidden": "true"})
        ]
        education_degree = [
            span_element.text.strip()
            for div_element in education_section.find_all('span', class_ = 't-14 t-normal')
            for span_element in div_element.find_all('span', attrs={"aria-hidden": "true"})
        ]
        combined_lists = list(zip(education_school, education_degree, education_time))
        education = {str(i): set(section) for i, section in enumerate(combined_lists)}

        return (name, company, location, education, link_candidates)
    @staticmethod
    def read_config(file_path):
        config = {}
        with open(file_path, 'r') as file:
            for line in file:
                key, value = line.strip().split(' = ')
                config[key.strip()] = value.strip()
        return config