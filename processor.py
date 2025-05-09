import pandas as pd
from scraper import DataScrape
from scraper import UserAgent
import re
import time

class Processor:

    def __init__(self, waitTime : int, headless : bool):
        self.waitTime = waitTime
        self.headless = headless

    def clean_excel_string(self, value):
        if isinstance(value, str):
            # Remove control characters (Excel cannot handle ASCII < 32 except \t \n \r)
            value = re.sub(r"[\x00-\x08\x0B\x0C\x0E-\x1F]", "", value)
        return value

    def start_processing(self):
        #current_URL = "https://www.congress.gov/search?q=%7B%22source%22%3A%22legislation%22%2C%22search%22%3A%22congressId%3A113+AND+billStatus%3A%5C%22Introduced%5C%22%22%7D&pageSize=25"
        #current_URL = "https://www.congress.gov/search?q=%7B%22source%22%3A%22legislation%22%2C%22search%22%3A%22congressId%3A113+AND+billStatus%3A%5C%22Introduced%5C%22%22%7D&pageSize=100"
        current_URL = "https://www.congress.gov/search?q=%7B%22source%22%3A%22legislation%22%2C%22search%22%3A%22congressId%3A113+AND+billStatus%3A%5C%22Introduced%5C%22%22%7D&pageSize=250"
        dataframe_container = []
        final_page = False
        current_count = 0
        
        if self.headless:
            UA = UserAgent()
            agents = UA.getUserAgents()

            print("Agents Successfully Located!")

            dataClass = DataScrape(self.headless, agents.pop())
        else:
            dataClass = DataScrape(self.headless, "")


        print("----------------------------------------------")
        print("-----------STARTING DATA EXTRACTION-----------")
        print("----------------------------------------------")

        print("ALGORITHM LOG:")
        while final_page != True :
            current_soup = dataClass.get_soup(current_URL)
            page_data_dict = dataClass.get_full_data_dict(current_soup, current_count, self.waitTime)

            page_dataframe = pd.DataFrame(page_data_dict)
            dataframe_container.append(page_dataframe)

            """
            next_page = dataClass.find_next_button(current_soup)
            if not next_page:
                final_page = True
            else:
                current_URL = "https://www.congress.gov" + next_page

            current_count += len(page_dataframe)    
            """

            ## REMOVE BELOW TO RETAIN RECURSION -- UNCOMMENT ANY OTHER LINES OF CODE ABOVE
            final_page = True

        print("\n" + "\n" "DATA EXTRACTION AND PARSING COMPLETE")
        print("Creating Excel Sheet..." + "\n" + "Please Wait...")
        time.sleep(2)

        merge_data = pd.concat(dataframe_container)    
        merge_data["Bill Title"] = merge_data["Bill Title"].apply(self.clean_excel_string)

        merge_data.to_excel("congress_bills.xlsx", index=False)

        print("EXCEL SHEET SUCCESSFULLY CREATED!")
        print("Script has successfully finished.")

