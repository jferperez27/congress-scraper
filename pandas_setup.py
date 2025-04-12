import pandas as pd
import main as m

# def create_simple_dataframe():

sample_data = {
    'Congressional Session' : ["117th Congress"],
    'Bill Number' : ["H.B.3791"]
}

page_data_dict = m.get_simple_data_dict()
page_data = pd.DataFrame(page_data_dict)

print(page_data.head())

#page_data.to_excel("congress_bills.xlsx", index=False)

