from time import sleep
import time
from parsel import Selector
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup
from crawler_utils import Crawler
import json

class JobSpiderCrawler:
    def __init__(self, driver_path='./driver/chromedriver_win.exe'):
        self.driver_path = driver_path
        self.crawler = Crawler()
        self.driver = self.crawler.load_chrome_web_driver(path=driver_path)
        self.driver.get("https://www.jobspider.com/job/resume-search.asp")

    def search_keyword(self, keyword):
        try:
            search = self.driver.find_element(By.ID,"Textbox1" )
            search.click()        
        except:
            pass

        input_field = self.driver.find_element(By.ID,"Textbox1" )
        input_field.send_keys(keyword)
        button = self.driver.find_element(By.ID,"Button1" )
        button.click()

    def get_list_cv(self, keyword):
        self.search_keyword(keyword)
        lst_candidates = []
        xpath = "/html/body/form/table[2]/tbody/tr/td[2]/table/tbody/tr[2]/td/table[2]/tbody/tr/td/center/table/tbody/tr/td/center/font/table" 
        elements = self.driver.find_elements(By.XPATH, xpath)
        for element in elements:
            inner_elements = element.find_elements(By.TAG_NAME, 'a')
            for inner_element in inner_elements:
                href = inner_element.get_attribute('href')
                if 'view-resume' in href:
                    lst_candidates.append(href)
        return lst_candidates

    def get_spider_info(self, link_candidates):
        self.driver.get(link_candidates)
        xpath_spider_id = "//font[contains(text(), 'SpiderID:')]"
        xpath_desired_job_location = "//font[contains(text(), 'Desired Job Location:')]"
        initialScroll = 0
        finalScroll = 1000
        spider_id_element = self.driver.find_element(By.XPATH, xpath_spider_id)
        desired_job_location_element = self.driver.find_element(By.XPATH, xpath_desired_job_location)
        name = spider_id_element.text.split(":")[1].strip()
        location = desired_job_location_element.text.split(":")[1].strip()
        self.driver.execute_script(f"window.scrollTo({initialScroll}, {finalScroll})")
        time.sleep(1.5)
        education = self.get_spider_education(link_candidates)
        company = self.get_spider_company(link_candidates)
        return (name, company, location, education, link_candidates)

    def get_spider_education(self, link_candidates):
        initialScroll = 0
        finalScroll = 1000
        self.driver.get(link_candidates)
        time.sleep(3)
        self.driver.execute_script(f"window.scrollTo({initialScroll}, {finalScroll})")
        education_xpath = "//b[contains(text(), 'Education:')]/following-sibling::font"
        education_element = self.driver.find_element(By.XPATH, education_xpath)
        education_text = education_element.text.strip()
        education_lines = education_text.split('\n')

        before_empty_strings = []
        after_empty_strings = []
        temp_list = []
        for item in education_lines:
            if item == '':
                if temp_list:
                    after_empty_strings.append(temp_list)
                    temp_list = []
            else:
                if "•" in item:
                    split_item = [part.strip() for part in item.split("•")]
                    temp_list.extend(split_item)
                else:
                    temp_list.append(item.strip())

        if temp_list:
            after_empty_strings.append(temp_list)

        json_data = {str(i): section for i, section in enumerate(after_empty_strings)}
        return json_data

    def get_spider_company(self, link_candidates):
        initialScroll = 0
        finalScroll = 1000
        self.driver.get(link_candidates)
        time.sleep(3)
        self.driver.execute_script(f"window.scrollTo({initialScroll}, {finalScroll})")
        experience_xpath = "//b[contains(text(), 'Experience:')]/following-sibling::font"
        experience_element = self.driver.find_element(By.XPATH, experience_xpath)
        experience_text = experience_element.text.strip()
        experience_lines = experience_text.split('\n')

        before_empty_strings = []
        after_empty_strings = []
        temp_list = []
        for item in experience_lines:
            if item == '':
                if temp_list:
                    after_empty_strings.append(temp_list)
                    temp_list = []
            else:
                if "•" in item:
                    split_item = [part.strip() for part in item.split("•")]
                    temp_list.extend(split_item)
                else:
                    temp_list.append(item.strip())

        if temp_list:
            after_empty_strings.append(temp_list)

        json_data = {str(i): section for i, section in enumerate(after_empty_strings)}
        return json_data['0'][1]
    @staticmethod
    def get_driver(driver, link):
        return driver.get(link)