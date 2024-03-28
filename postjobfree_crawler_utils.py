from time import sleep
import time
from parsel import Selector
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup
from crawler_utils import Crawler
from selenium.common.exceptions import NoSuchElementException
import json

class PostJobFreeCrawler:
    def __init__(self, driver_path='./driver/chromedriver_win.exe'):
        self.driver_path = driver_path
        self.crawler = Crawler()
        self.driver = self.crawler.load_chrome_web_driver(path=driver_path)
        self.driver.get("https://www.postjobfree.com/")

    def search_keyword(self, keyword, location = ''):
        search = self.driver.find_element(By.ID, 'q')
        search.click()
        search.send_keys(keyword)
        search_location = self.driver.find_element(By.ID, 'l')
        search_location.click()
        search.send_keys(location)
        resume_click = self.driver.find_element(By.ID, 'ResumeLink')
        resume_click.click()

    def get_list_cv(self, keyword, location='', max_step = 100000):
        self.search_keyword(keyword, location= location)
        list_candidates = []
        step = 0
        while step < max_step:
            step +=1
            list_a = self.driver.find_elements(By.CLASS_NAME, "snippetPadding")
            list_candidates.extend([link.find_element(By.TAG_NAME, 'a').get_attribute("href") for link in list_a])
            try:
                snippet_element = self.driver.find_element(By.XPATH, "//div[@style='text-align:center;padding-top:15px; margin:5px;font-size:large;']")
                next_link = snippet_element.find_element(By.XPATH, "//a[text()='Next']")
                next_link.click()
            except NoSuchElementException:
                break
        return list_candidates


    def get_info(self, link_candidates):
        self.driver.get(link_candidates)
        snippet_element = self.driver.find_element(By.XPATH, "//div[@class='innercontent']")
        location_div = snippet_element.find_element(By.XPATH, "//div[@class='labelHeader'][contains(text(), 'Location:')]")
        location_a_tag = location_div.find_element(By.XPATH, "./following-sibling::a[@class='colorLocation']")
        location_name = location_a_tag.text


        resume_heading = snippet_element.find_element(By.XPATH, "//h4[contains(text(), 'Resume:')]")
        resume_div = resume_heading.find_element(By.XPATH, "./following-sibling::div[@class='normalText']")
        name_paragraph = resume_div.find_element(By.TAG_NAME, 'p')
        name = name_paragraph.text

        paragraphs = snippet_element.find_elements(By.TAG_NAME, 'p')
        company_name = None
        for index, paragraph in enumerate(paragraphs):
            if 'experience' in paragraph.text.lower():
                company_paragraph = paragraphs[index + 1]
                company_name = company_paragraph.text
                break

        education = None
        for index, paragraph in enumerate(paragraphs):
            if 'education' in paragraph.text.lower():
                education_paragraph = paragraphs[index + 1]
                education = education_paragraph.text
                break
        parts = education.split("/")
        education_name = {"0": [f"{parts[1].strip()}", f"{parts[0].strip()}, {parts[2].strip()}"]}

        return (name, company_name, location_name, education_name, link_candidates)
