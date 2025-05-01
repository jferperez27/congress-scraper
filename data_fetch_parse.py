from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from collections import deque
import requests

class UserAgent:
    def getUserAgents(self):
        url = "https://explore.whatismybrowser.com/useragents/explore/software_name/chrome/"
        driver = webdriver.Chrome()
        driver.get(url)
        output = []

        try:
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CLASS_NAME, "corset")))
        except:
            print("Timeout waiting for page to load.")
            print("Attempting to retry...")
            driver.quit()    
            return self.getUserAgents()
    
        html = driver.page_source

        soup = BeautifulSoup(html, 'html.parser')
        for item in soup.find_all(class_='code'):
            item = item.text.strip()
            if item is not None:
                output.append(item)
        driver.quit()

        return output


class DataScrape:

    def __init__(self, headless : bool, agent : str):
        self.headless = headless
        self.agent = agent
        self.driver = self._init_driver()
        self.scrape_count = 0
        self.headers = {
            "User-Agent" : self.agent
        }

    def _init_driver(self):
        options = Options()
        if self.headless:
            options.add_argument("--headless=new")
            options.add_argument("user-agent=" + self.agent)
        prefs = {"profile.managed_default_content_settings.images": 2,
                "profile.managed_default_content_settings.stylesheets": 2,
                "profile.managed_default_content_settings.fonts": 2}
        options.add_experimental_option("prefs", prefs)
        return webdriver.Chrome(options=options)

    def scrape_html(self, url : str):
        """
        Uses Selenium API to open Chromium and fetch HTML data, returns HTML.
        """
        self.driver.set_page_load_timeout(5)

        self.driver.execute_cdp_cmd("Network.setBlockedURLs", {
            "urls": ["*.png", "*.jpg", "*.jpeg", "*.gif", "*.css", "*.woff", "*.ttf", "*.svg"]})
        self.driver.execute_cdp_cmd("Network.enable", {})

        ## Waits for page to fully load before scraping HTML
        try:
            self.driver.get(url)

            # Wait until the results section loads or overview (adjust class if needed)
            WebDriverWait(self.driver, 3).until(
                EC.any_of(
                EC.presence_of_element_located((By.CLASS_NAME, "next")), 
                EC.presence_of_element_located((By.CLASS_NAME, "overview_label")))
            )
        
            main = self.driver.current_window_handle
            for windows in self.driver.window_handles:
                if windows != main:
                    self.driver.switch_to.window(windows)
                    self.driver.close()
                    self.driver.delete_all_cookies()
            self.driver.switch_to.window(main)

            ## Scrapes HTML, quits Selenium (Chromium)
            html = self.driver.page_source
            #self.driver.quit()
            self.scrape_count += 25
            if self.scrape_count == 10:
                self.driver.quit()
                self.driver = self._init_driver()
                self.scrape_count = 0
            return html
        except:
            print("Timeout waiting for page to load.")
            print("Attempting to retry...")
            self.driver.quit()    
            self.driver = self._init_driver()
            return self.scrape_html(url)

    def get_soup(self, url : str):
        """
        Scrapes HTML from inputted URL, returns Beautified HTML for easy search and traversal.
        """
        return BeautifulSoup(self.scrape_html(url), 'html.parser')

    def parse_simple_data(self, bill_titles, bill_desc, bill_status):
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
            if (increment % 2 == 0):
                status_formatted = bill_status[increment].text.split('Here')[0].strip()
                status_only = status_formatted.split("status ")[1]
                bill_data.append(status_only)
                bill_data.append(bill_desc[increment].text.strip())
                bill_data.append(title_formatted[0])
                bill_data.append(title_formatted[1])
                data.append(bill_data)
                current_count += 1
            increment += 1
        return data    

    def get_additional_info(self, bill_page):
        output = []
        #url = bill_page
        print(bill_page)
        #soup = self.get_soup(url)
        soup = self.get_bill_detail_requests(bill_page)

        sponsor = soup.find(class_='standard01')
        output.append(sponsor.find("a").text.strip())

        return output

    def get_additional_info_ex(self, bill_page):
        """

        """
        output = []
        url = bill_page
        print(bill_page)
        soup = self.get_soup(url)

        sponsor = soup.find(class_='standard01')
        output.append(sponsor.find("a").text.strip())
        table = sponsor.find_all("tr")

        count = 0
        for item in table:

            header = item.find('td')
            committee_header = item.find('th')
            if header is not None:
                if count == 1:
                    committee = header.text.strip()
                    committee_label = committee_header.get_text(strip=True)
                    if committee_header and committee_label == "Committees:":
                        output.append(committee)
                    else:
                        output.append("No Starting Committee")

            count += 1

        return output

    def get_full_data_dict(self, soup : BeautifulSoup, count : int) -> dict:
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
            "Bill Committee" : [],
            "Bill Status" : []
            #"Text of Bill" : []
        }

        bill_title = soup.find_all(class_='result-heading') # Bill title, number, congressional session
        bill_desc = soup.find_all(class_='result-title') # Bill description
        bill_status = soup.find_all(class_='result-item result-tracker') # Bill status
        bill_urls = self.get_bill_pages(bill_title)
        data_list = self.parse_simple_data(bill_title, bill_desc, bill_status)
        # data_list order:
        # - bill status
        # - bill description/title
        # - bill number/type
        # - congressional session

        count = count
        for data in data_list:
            current_url = bill_urls.popleft()
            expanded_data = self.get_additional_info_ex(current_url)
            data_dict["Count"].append(str(count))
            data_dict["Congressional Session"].append(data[3])
            data_dict["Bill Type & Number"].append(data[2])
            data_dict["Bill Title"].append(data[1])
            data_dict["Bill Sponsor"].append(expanded_data[0])
            data_dict["Bill Committee"].append(expanded_data[1])
            data_dict["Bill Status"].append(data[0])
            count += 1
        return data_dict


    def find_next_button(self, soup : BeautifulSoup):
        button_element = soup.find_all(class_= 'next')
        
        if not button_element:
            print(soup)
            print('no further pages to search ... ending retrieval')
            return None
        button_link = button_element[0].get('href')
        print(button_link)
        return button_link

    def get_bill_pages(self, result_heading_collection):
        output = deque([])
        increment = 0

        for item in result_heading_collection:
            if increment % 2 == 0:
                bill_page = "https://www.congress.gov" + item.find("a")["href"]
                output.append(bill_page)
            increment += 1

        return output



    def fetch_info(self):
        return self.get_additional_info_ex("https://www.congress.gov/bill/113th-congress/senate-bill/1800/cosponsors?s=1&r=3&q=%7B%22search%22%3A%22congressId%3A113+AND+billStatus%3A%5C%22Introduced%5C%22%22%7D")
if __name__ == "__main__":
    # Example usage of DataScrape
    scraper = DataScrape(headless=True, agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36")
    scraper.fetch_info()