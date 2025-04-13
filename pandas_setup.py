import pandas as pd
import main as m
import time
import re

# def create_simple_dataframe():


# url = "https://www.congress.gov/search?q=%7B%22source%22%3A%22legislation%22%2C%22search%22%3A%22congressId%3A113+AND+billStatus%3A%5C%22Introduced%5C%22%22%7D"
# second_url = "https://www.congress.gov" + "/search?q=%7B%22source%22%3A%22legislation%22%2C%22search%22%3A%22congressId%3A113+AND+billStatus%3A%5C%22Introduced%5C%22%22%7D&page=2"
# page_data_dict = m.get_simple_data_dict(url)
# page_data = pd.DataFrame(page_data_dict)

# page_two_data_dict = m.get_simple_data_dict(second_url)
# second_page_data = pd.DataFrame(page_two_data_dict)

# merge_data = pd.concat([page_data, second_page_data], ignore_index=True)

# print(len(second_page_data))
# print(len(merge_data))

#page_data.to_excel("congress_bills.xlsx", index=False)


def clean_excel_string(value):
    if isinstance(value, str):
        # Remove control characters (Excel cannot handle ASCII < 32 except \t \n \r)
        value = re.sub(r"[\x00-\x08\x0B\x0C\x0E-\x1F]", "", value)
    return value

def get_113th_congress_spreadsheet():
    current_URL = "https://www.congress.gov/search?q=%7B%22source%22%3A%22legislation%22%2C%22search%22%3A%22congressId%3A113+AND+billStatus%3A%5C%22Introduced%5C%22%22%7D&pageSize=250"
    dataframe_container = []
    final_page = False
    current_count = 0

    while final_page != True :
        current_soup = m.get_soup(current_URL)
        #time.sleep(3)
        page_data_dict = m.get_simple_data_dict(current_soup, current_count)
        page_dataframe = pd.DataFrame(page_data_dict)
        dataframe_container.append(page_dataframe)

        next_page = m.find_next_button(current_soup)
        if not next_page:
            final_page = True
        else:
            current_URL = "https://www.congress.gov" + next_page

        current_count += len(page_dataframe)    

    merge_data = pd.concat(dataframe_container)    
    merge_data["Bill Description"] = merge_data["Bill Description"].apply(clean_excel_string)

    print(len(merge_data))      
    merge_data.to_excel("congress_bills.xlsx", index=False)

get_113th_congress_spreadsheet()
