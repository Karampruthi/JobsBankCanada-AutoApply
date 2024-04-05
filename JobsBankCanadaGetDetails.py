from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from datetime import datetime
from webdriver_manager.chrome import ChromeDriverManager
import time
import pandas as pd

# Load previously applied jobs to avoid duplicates
applied_jobs = pd.read_csv('jobbank.csv')
jobs_dict = {}

# Keywords and province for job search
keywords = ['data', 'analyst', 'software', 'python']
province = 'ON'
format_string = "%B %d, %Y"  # Date format for parsing
search_date = datetime.strptime('March 10, 2024', format_string).date()

# Selenium browser options setup
options = Options()
options.add_experimental_option('detach', True)

# Initialize WebDriver for Chrome
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

# Construct search URL with keywords and province, navigate to it
search_terms = '+'.join(keywords)
driver.get(f'https://www.jobbank.gc.ca/jobsearch/jobsearch?fcid=1455&fcid=1464&fcid=1465&fcid=3763&fcid=3770&fcid=3776&fcid=3949&fcid=3950&fcid=296001&fcid=296804&fn21=21231&fn21=21232&term={search_terms}&page=1&sort=D&fprov={province}&fsrc=16')

# Click the 'Date posted' link
WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.LINK_TEXT, "Date posted"))).click()

# Initialize list for storing job info
articles_info = []

while True:
    # Wait for job listings to load and collect them
    job_listings = WebDriverWait(driver, 10).until(EC.presence_of_all_elements_located((By.TAG_NAME, "article")))
    for job in job_listings:
        article_id = job.get_attribute('id').split('-')[-1]
        posted_date_text = job.find_element(By.CLASS_NAME, "date").text
        posted_date = datetime.strptime(posted_date_text, format_string).date()
        if posted_date < search_date:
            break
        articles_info.append((article_id, posted_date))
    if posted_date < search_date:
        break
    # Click to load more results and ensure new jobs have loaded
    WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.ID, "moreresultbutton"))).click()
    WebDriverWait(driver, 10).until(lambda d: len(d.find_elements(By.TAG_NAME, "article")) > len(job_listings))

# Process each job, skipping already applied ones
for article_id, posted_date in articles_info:
    if article_id in applied_jobs['job_id'].values:
        continue

    driver.get(f'https://www.jobbank.gc.ca/jobsearch/jobposting/{article_id}?source=searchresults')
    
    try:
        # Extract job requirements and details
        requirements_dict = {
            'Position': driver.find_element(By.XPATH, "//span[@property='title']").text,
            'Posted Date': posted_date,
            'Extracted Date': datetime.now().date()
        }
        
        requirements_container = WebDriverWait(driver, 2).until(
            EC.presence_of_element_located((By.CLASS_NAME, "job-posting-detail-requirements"))
        )
        headers = requirements_container.find_elements(By.XPATH, ".//h4")
        for header in headers:
            key = header.text.strip()
            value_element = header.find_element(By.XPATH, "following-sibling::*[1]")
            requirements_dict[key] = value_element.text.strip().split('\n')

        # Click the apply button and extract application info
        apply_button = driver.find_element(By.ID, "applynowbutton")
        driver.execute_script("arguments[0].scrollIntoView(true);", apply_button)
        apply_button.click()
        
        WebDriverWait(driver, 10).until(EC.visibility_of_element_located((By.ID, "applynow")))
        apply_container = driver.find_element(By.ID, "applynow")
        apply_container_lines = apply_container.text.split('\n')
        
        email_index = apply_container_lines.index('By email') + 1
        requirements_dict['Email'] = apply_container_lines[email_index]
        requirements_dict['job_instructions'] = apply_container_lines[email_index+1:]
        
        jobs_dict[article_id] = requirements_dict
    except (TimeoutException, NoSuchElementException):
        continue

# Close the WebDriver
driver.quit()

# Convert collected job info to DataFrame and update CSV
df = pd.DataFrame.from_dict(jobs_dict, orient='index')
df.reset_index(inplace=True)
df = df.rename(columns={'index': 'job_id'})
df = df[df['Email'] != 'ValueError']  # Filter out jobs with invalid email
new_df = pd.concat([df, applied_jobs]).drop_duplicates(subset='job_id', keep='first')
new_df.to_csv('jobbank.csv', index=False)

