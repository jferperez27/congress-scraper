from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from collections import deque


def scrape_html(url : str):
    driver = webdriver.Chrome()
    driver.get(url)
    try:
        # Wait until the results section loads (adjust class if needed)
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
    html = driver.page_source
    driver.quit()
    return html

def get_soup(url : str):
    return BeautifulSoup(scrape_html(url), 'html.parser')

def get_additional_info(bill_page):
    output = []
    url = bill_page
    print(bill_page)
    soup = get_soup(url)

    sponsor = soup.find(class_='standard01')
    output.append(sponsor.find("a").text.strip())

    return output



def parse_simple_data(bill_titles, bill_desc, bill_status):
    """
    Parses the HTML data and prints out the title, description, and status of each bill.
    """
    increment = 0 # Skips every second bill title to get "expanded view" of the bill
    current_count = 0 # To reference the current iteration of bill description and status
    data = []

    ## Loops through the search results and prints out the title and description of each bill.
    for title in bill_titles:
        bill_data = [] ## Stores output
        title_formatted = title.text.split('— ') ## Gets Bill Title and Congressional Session
        #bill_page = title.find("a")["href"] ## Gets link for additional bill information
        #supplementary_info = get_additional_info(bill_page)
        if (increment % 2 == 0):
            status_formatted = bill_status[increment].text.split('Here')[0].strip()
            status_only = status_formatted.split("status ")[1]
            # print("------------------------------------------------")
            # print("Count : " + str(current_count + 1))
            # print("Congresional Session: ")
            # print(title_formatted[1])
            # print("Bill Type & Number: ")
            # print(title_formatted[0])
            # print("Bill Sponsor: ")
            # print(supplementary_info[0])
            # print("Bill Description: ")
            # print(bill_desc[increment].text.strip())
            # print("Bill Status: ")
            # print(status_only)
            bill_data.append(status_only)
            bill_data.append(bill_desc[increment].text.strip())
            bill_data.append(title_formatted[0])
            bill_data.append(title_formatted[1])
            #data.insert(current_count, bill_data)
            data.append(bill_data)
            current_count += 1
        increment += 1
    return data    

def get_first_bill_heading():
    url = "https://www.congress.gov/search?q=%7B%22source%22%3A%22legislation%22%2C%22search%22%3A%22congressId%3A113+AND+billStatus%3A%5C%22Introduced%5C%22%22%7D"
    soup = get_soup(url)
    bill_title = soup.find_all(class_='result-heading') # Bill title, number, congressional session
    formatted = bill_title[0].text.split('- ')

    for bill_info in bill_title:
        print("https://www.congress.gov" + bill_info.find("a")["href"])

    bill_page = bill_title[0].find("a")["href"] ## Gets link for additional bill information
    supplementary_info = get_additional_info(bill_page)
    print(formatted[0])
    print(supplementary_info[0])
    return formatted[0]


def get_simple_data_dict(soup : BeautifulSoup, count : int) -> dict:
    data_dict = {
        "Count" : [],
        "Congressional Session" : [],
        "Bill Type & Number" : [],
        "Bill Description" : [],
        "Bill Status" : []
    }
    #soup = get_soup(url)
    bill_title = soup.find_all(class_='result-heading') # Bill title, number, congressional session
    bill_desc = soup.find_all(class_='result-title') # Bill description
    bill_status = soup.find_all(class_='result-item result-tracker') # Bill status
    data_list = parse_simple_data(bill_title, bill_desc, bill_status)
    # data_list order:
    # - bill status
    # - bill description/title
    # - bill number/type
    # - congressional session

    count = count
    for data in data_list:
        data_dict["Count"].append(str(count))
        data_dict["Congressional Session"].append(data[3])
        data_dict["Bill Type & Number"].append(data[2])
        data_dict["Bill Description"].append(data[1])
        data_dict["Bill Status"].append(data[0])
        count += 1
    return data_dict

def get_full_data_dict(soup : BeautifulSoup, count : int) -> dict:
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

    #print(output)
    return output


if __name__ == "__oops__":
    #get_first_bill_heading()
    url = "https://www.congress.gov/search?q=%7B%22source%22%3A%22legislation%22%2C%22search%22%3A%22congressId%3A113+AND+billStatus%3A%5C%22Introduced%5C%22%22%7D"
    soup = get_soup(url)
    bill_title = soup.find_all(class_='result-heading') # Bill title, number, congressional session
    pages = get_bill_pages(bill_title)

    print(pages.popleft())
    print(pages)