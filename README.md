# Crawling data

## 1. Requirement
- Python version 3.10
- Chrome version 122
- BeautifulSoup4
- lxml
- pandas
- selenium
- parsel
- Apache Airflow
- Chromedriver (is stored at `driver` folder, with 2 file: `chromedriver` for Macbook M1 and `chromedriver_win.exe` for win64)

## 2. Source

The project crawls candidate resumes from the following sources:

- [LinkedIn](https://www.linkedin.com)
- [PostJobFree](https://www.postjobfree.com)
- [JobSpider](https://www.jobspider.com)

## 3. Data Schema

Below is the schema for the data being used in the project:

| Field Name        | Data Type  | Description                        |
|-------------------|------------|------------------------------------|
| name              | TEXT       | Candidate name                     |
| company           | TEXT       | Current company                    |
| location          | TEXT       | Current or desired location        |
| education         | JSON       | Education background               |
| link_candidates   | TEXT       | Link to resume or personal profile |

## 4. Crawling Script
### a. LinkedIn.com
- The crawling script for LinkedIn is stored in `CrawlerUtils.py`.
- Since LinkedIn requires login credentials, make sure to provide `linkedin_username` and `linkedin_password` in the `config.txt` file.
- In the `main.py` file, `extract_linkedin_data()` is created to run and retrieve the list of candidate information.

### b. JobSpider.com
- The crawling script for JobSpider is stored in `jobspider_crawler_utils.py`.
- This script inherits the `Crawler()` class to create the Selenium driver.
- In the `main.py` file, `extract_jobspider_data()` is created to run and retrieve the list of candidate information.

### c. PostJobFree.com
- The crawling script for PostJobFree is stored in `postjobfree_crawler_utils.py`.
- Similar to JobSpider, this script also inherits the `Crawler()` class to create the Selenium driver.
- In the `main.py` file, `extract_postjobfree_data()` is created to run and retrieve the list of candidate information.

## 5. Suggestion for scheduling on Airflow
This code defines an Airflow DAG named 'data_extraction' that runs data extraction from three sources: LinkedIn, JobSpider, and PostJobFree.
-Four PythonOperator tasks are defined:
  - `extract_linkedin_task`: Calls the extract_linkedin_data function.
  - `extract_jobspider_task`: Calls the extract_jobspider_data function.
  - `extract_postjobfree_task`: Calls the extract_postjobfree_data function.
  - `store_data_task`: Calls the store_data function to store extracted data. It takes XComs (cross-communication messages) from the previous three tasks as arguments.

Task Dependencies:
  - `store_data_task` waits for all three extraction tasks to run parallelly and be completed before executing.
