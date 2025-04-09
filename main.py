from bs4 import BeautifulSoup
from selenium import webdriver

## Prompts Selenium to navigate to the first page of Congress.gov results for the 119th Congress, scrapes the HTML under the "html" variable.
url = "https://www.congress.gov/search?pageSort=dateOfIntroduction%3Adesc&pageSize=25&q=%7B%22source%22%3A%22legislation%22%2C%22search%22%3A%22congressId%3A119+AND+billStatus%3A%5C%22Introduced%5C%22%22%2C%22congress%22%3A%22all%22%7D"
driver = webdriver.Chrome()
driver.get(url)
html = driver.page_source

## Parses the HTML with BeautifulSoup.
soup = BeautifulSoup(html, 'html.parser')
bill_title = soup.find_all(class_='result-heading') # Bill title, number, congressional session
bill_desc = soup.find_all(class_='result-title') # Bill description
bill_status = soup.find_all(class_='result-item result-tracker') # Bill status


def parse_simple_data():
    """
    Parses the HTML data and prints out the title, description, and status of each bill.
    """
    increment = 0 # Skips every second bill title to get "expanded view" of the bill
    current_count = 0 # To reference the current iteration of bill description and status

    ## Loops through the search results and prints out the title and description of each bill.
    for title in bill_title:
        title_formatted = title.text.split('— ')
        if (increment % 2 == 0):
            status_formatted = bill_status[current_count].text.split('Here')[0].strip()
            status_only = status_formatted.split("status ")[1]
            print("------------------------------------------------")
            print("Congresional Session: ")
            print(title_formatted[1])
            print("Bill Type & Number: ")
            print(title_formatted[0])
            print("Bill Description: ")
            print(bill_desc[increment].text.strip())
            print("Bill Status: ")
            print(status_only)
            current_count += 1
        increment += 1

parse_simple_data()