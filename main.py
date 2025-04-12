from bs4 import BeautifulSoup
from selenium import webdriver

## Prompts Selenium to navigate to the first page of Congress.gov results for the 119th Congress, scrapes the HTML under the "html" variable.
url = "https://www.congress.gov/search?q=%7B%22source%22%3A%22legislation%22%2C%22search%22%3A%22congressId%3A113+AND+billStatus%3A%5C%22Introduced%5C%22%22%7D"

def scrape_html():
    driver = webdriver.Chrome()
    driver.get(url)
    html = driver.page_source
    return html

def get_soup():
    return BeautifulSoup(scrape_html(), 'html.parser')

def parse_simple_data(bill_titles, bill_desc, bill_status):
    """
    Parses the HTML data and prints out the title, description, and status of each bill.
    """
    increment = 0 # Skips every second bill title to get "expanded view" of the bill
    current_count = 0 # To reference the current iteration of bill description and status
    data = []

    ## Loops through the search results and prints out the title and description of each bill.
    for title in bill_titles:
        bill_data = []
        title_formatted = title.text.split('— ')
        if (increment % 2 == 0):
            status_formatted = bill_status[increment].text.split('Here')[0].strip()
            status_only = status_formatted.split("status ")[1]
            # print("------------------------------------------------")
            # print("Count : " + str(current_count + 1))
            # print("Congresional Session: ")
            # print(title_formatted[1])
            # print("Bill Type & Number: ")
            # print(title_formatted[0])
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
    soup = get_soup()
    bill_title = soup.find_all(class_='result-heading') # Bill title, number, congressional session
    formatted = bill_title[0].text.split('- ')
    return formatted[0]

# if __name__ == '__main__':
#     soup = get_soup()
#     bill_title = soup.find_all(class_='result-heading') # Bill title, number, congressional session
#     bill_desc = soup.find_all(class_='result-title') # Bill description
#     bill_status = soup.find_all(class_='result-item result-tracker') # Bill status
#     parse_simple_data(bill_title, bill_desc, bill_status)

def get_simple_data_dict() -> dict:
    data_dict = {
        "Count" : [],
        "Congressional Session" : [],
        "Bill Type & Number" : [],
        "Bill Description" : [],
        "Bill Status" : []
    }
    soup = get_soup()
    bill_title = soup.find_all(class_='result-heading') # Bill title, number, congressional session
    bill_desc = soup.find_all(class_='result-title') # Bill description
    bill_status = soup.find_all(class_='result-item result-tracker') # Bill status
    data_list = parse_simple_data(bill_title, bill_desc, bill_status)
    # data_list order:
    # - bill status
    # - bill description/title
    # - bill number/type
    # - congressional session

    count = 1
    for data in data_list:
        data_dict["Count"].append(str(count))
        data_dict["Congressional Session"].append(data[3])
        data_dict["Bill Type & Number"].append(data[2])
        data_dict["Bill Description"].append(data[1])
        data_dict["Bill Status"].append(data[0])
        count += 1
    return data_dict

