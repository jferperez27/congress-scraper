from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from collections import deque


def scrape_html(url : str):
    """
    Uses Selenium API to open Chromium and fetch HTML data, returns HTML.
    """

    ## Initializes Chromium
    driver = webdriver.Chrome()
    driver.get(url)

    ## Waits for page to fully load before scraping HTML
    try:
        # Wait until the results section loads or overview (adjust class if needed)
        WebDriverWait(driver, 10).until(
            EC.any_of(
            EC.presence_of_element_located((By.CLASS_NAME, "next")), 
            EC.presence_of_element_located((By.CLASS_NAME, "overview_label")))
        )
    except:
        print("Timeout waiting for page to load.")
        print("Attempting to retry...")
        driver.quit()    
        return scrape_html(url)
    
    ## Scrapes HTML, quits Selenium (Chromium)
    html = driver.page_source
    driver.quit()
    return html

def get_soup(url : str):
    """
    Scrapes HTML from inputted URL, returns Beautified HTML for easy search and traversal.
    """
    return BeautifulSoup(scrape_html(url), 'html.parser')

def get_additional_info(bill_page):
    output = []
    url = bill_page
    print(bill_page)
    soup = get_soup(url)

    sponsor = soup.find(class_='standard01')
    output.append(sponsor.find("a").text.strip())

    return output

def get_full_data_dict(soup : BeautifulSoup, count : int) -> dict:
    """
    Creates a dictionary with all data. Using BeautifulSoup to traverse the HTML
    data scraped using Selenium, the function searches for all specified data in 
    HTML and inputs it onto its corresponding dictionary key for O(1) retrieval.

    Inputs: Beginning URL for Congress.gov search traversal.
    Outputs: Dictionary containing all relevant information for Excel Sheets.
    """

    data_dict = {
        "Count" : [],
        "Congressional Session" : [],
        "Bill Type & Number" : [],
        "Bill Title" : [],
        "Bill Sponsor" : [],
        #"Bill Co-Sponsor(s)" : [],
        #"Bill Summary" : [],
        #"Bill Committee" : [],
        "Bill Status" : []
        #"Text of Bill" : []
    }

    bill_title = soup.find_all(class_='result-heading') # Bill title, number, congressional session
    bill_desc = soup.find_all(class_='result-title') # Bill description
    bill_status = soup.find_all(class_='result-item result-tracker') # Bill status
    bill_urls = get_bill_pages(bill_title)
    data_list = parse_simple_data(bill_title, bill_desc, bill_status)
    # data_list order:
    # - bill status
    # - bill description/title
    # - bill number/type
    # - congressional session

    count = count
    for data in data_list:
        current_url = bill_urls.popleft()
        expanded_data = get_additional_info(current_url)
        data_dict["Count"].append(str(count))
        data_dict["Congressional Session"].append(data[3])
        data_dict["Bill Type & Number"].append(data[2])
        data_dict["Bill Title"].append(data[1])
        data_dict["Bill Sponsor"].append(expanded_data[0])
        data_dict["Bill Status"].append(data[0])
        count += 1
    return data_dict


def find_next_button(soup : BeautifulSoup):
    button_element = soup.find_all(class_= 'next')
    
    if not button_element:
        print(soup)
        print('no further pages to search ... ending retrieval')
        return None
    button_link = button_element[0].get('href')
    print(button_link)
    return button_link

def get_bill_pages(result_heading_collection):
    output = deque([])
    increment = 0

    for item in result_heading_collection:
        if increment % 2 == 0:
            bill_page = "https://www.congress.gov" + item.find("a")["href"]
            output.append(bill_page)
        increment += 1

    return output