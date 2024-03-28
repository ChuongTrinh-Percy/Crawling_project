#%%
import imp
import re
import sys
from time import sleep
import sqlite3
from parsel import Selector
from selenium import webdriver
from crawler_utils import Crawler
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup
from jobspider_crawler_utils import JobSpiderCrawler
from postjobfree_crawler_utils import PostJobFreeCrawler
imp.reload(sys)


def extract_linkedin_data():
    crawler = Crawler() 
    linkedin_data = []
    config = crawler.read_config(file_path = 'config.txt')
    linkedin_username = config.get('username')
    linkedin_password = config.get('password')

    crawler = Crawler(linkedin_username , linkedin_password)
    path = './driver/chromedriver_win.exe'
    driver = crawler.load_chrome_web_driver(path=path)
    driver.get('https://www.linkedin.com/login?trk=guest_homepage-basic_nav-header-signin')

    list_candidates = crawler.get_list_candidates(driver, keyword= "data", max_value = 10)
    step = 0 
    for cadidate in list_candidates:
        step +=1
        try: 
            linkedin_data.append(crawler.get_info(driver, cadidate))
        except:
            pass
        if step == 150:
            break
    return linkedin_data


def extract_jobspider_data():
    jobspidercrawler = JobSpiderCrawler()
    jobspider_data = []
    list_candidates_spider = jobspidercrawler.get_list_cv('data')
    step = 0 
    for cadidate in list_candidates_spider:
        step +=1
        try:
            jobspider_data.append(jobspidercrawler.get_spider_info(cadidate))
        except:
            pass
        if step == 150:
            break
    return jobspider_data


def extract_postjobfree_data():
    postjobfreecrawler = PostJobFreeCrawler()
    postjob_data= []
    step = 0 
    list_candidates_postjobfree = postjobfreecrawler.get_list_cv('data','', max_step= 10)
    for cadidate in list_candidates_postjobfree:
        step +=1
        try:
            postjob_data.append(postjobfreecrawler.get_info(cadidate))
        except:
            pass
        if step == 150:
            break
    return postjob_data

def store_data(linkedin_data, jobspider_data, postjobfree_data):
    linkedin_candidates = linkedin_data
    jobspider_candidates = jobspider_data
    postjobfree_candidates = postjobfree_data

    conn = sqlite3.connect('candidate_data.db')
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS candidates
                      (name TEXT, company TEXT, location TEXT, education TEXT)''')

    for candidate in linkedin_candidates:
        cursor.execute("INSERT INTO candidates VALUES (?, ?, ?, ?)", 
                       (candidate['name'], candidate['company'], candidate['location'], candidate['education']))
    
    for candidate in jobspider_candidates:
        cursor.execute("INSERT INTO candidates VALUES (?, ?, ?, ?)", 
                       (candidate['name'], candidate['company'], candidate['location'], candidate['education']))
    
    for candidate in postjobfree_candidates:
        cursor.execute("INSERT INTO candidates VALUES (?, ?, ?, ?)", 
                       (candidate['name'], candidate['company'], candidate['location'], candidate['education']))
    conn.commit()
    conn.close()

    print("Data stored successfully.")

#%%
# if __name__ == "__main__":
linkedin = extract_linkedin_data()
job_spider = extract_jobspider_data()
postjobfree = extract_postjobfree_data()
