#!/usr/bin/env python
# coding: utf-8

# In[1]:


# Import necessary libraries
from bs4 import BeautifulSoup
import pandas as pd
import numpy as np
import requests
from datetime import datetime


# In[2]:


# Set display options for Pandas DataFrame
pd.set_option('display.max_columns', 500)
pd.set_option('display.max_rows', 500)


# In[3]:


# Define the URL
URL = 'https://tradingeconomics.com/forecast/commodity'


# In[4]:


#Somtimes you might get error so try adding a browser user agent.
#https://deviceatlas.com/blog/list-of-user-agent-strings


# In[5]:


# Define request headers
headers = {
    "Connection": "keep-alive",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.121 Safari/537.36"
}


# In[6]:


# Function to extract and clean data from the webpage
def extract_and_clean_data(response):
    if response.status_code != 200:
        print("Failed to fetch the webpage.")
        return None
    
    # Parse the HTML content using BeautifulSoup
    soup = BeautifulSoup(response.text, 'html.parser')

    # Find the table containing the data
    table = soup.find_all('table')[0]

    # Extract column titles and clean the list
    table_headers = table.find_all('th')    
    table_titles = [title.text.strip() for title in table_headers if title.text.strip() != 'Signal']
    table_titles = list(filter(None,table_titles))

    # Extract and clean data cells
    column_data = soup.find_all('td')
    data = [row.text.strip() for row in column_data]
    data = list(filter(None, data))

    # Calculate header length and number of rows
    lenofheader = len(table_titles)
    lenofrows = len(data) // lenofheader

    # Reshape data into a 2D array and create a DataFrame
    a = np.reshape(data, (lenofrows, lenofheader))
    df = pd.DataFrame(a, columns=table_titles)
    
    return df


# In[7]:


# Function to reshape and clean data
def reshape_data(df):
    # Define a dictionary for mapping quarter starts
    quarter_starts = {'Q1': '01', 'Q2': '04', 'Q3': '07', 'Q4': '10'}
    new_column_names = []
    
    # Generate new column names based on quarters
    for col in df.columns[2:]:
        quarter = quarter_starts[col.split('/')[0]]
        year = '20' + col.split('/')[1]
        new_column_names.append(year + quarter)
    
    # Update DataFrame column names
    df.columns = list(df.columns[:2]) + new_column_names
    
    # Drop the 'Price' column
    df = df.drop(columns=['Price'])
    
    # Melt the DataFrame to reshape it
    df = df.melt(id_vars=["Energy"], var_name="Date", value_name="Rates")
    
    return df


# In[8]:


# Function to create new rows with dates shifted by one and two months
def duplicate_and_change_date(row):
    new_row1 = row.copy()
    new_row2 = row.copy()
    date_obj = pd.to_datetime(row['Date'], format='%Y%m')
    new_row1['Date'] = (date_obj + pd.DateOffset(months=1)).strftime('%Y%m')
    new_row2['Date'] = (date_obj + pd.DateOffset(months=2)).strftime('%Y%m')
    return [new_row1, new_row2]


# In[9]:


# Main execution
response = requests.get(URL, headers=headers)
df = extract_and_clean_data(response)

if df is not None:
    df = reshape_data(df)
    duplicated_df = pd.DataFrame([item for sublist in df.apply(duplicate_and_change_date, axis=1) for item in sublist])
    result_df = pd.concat([df, duplicated_df], ignore_index=True)
    print('\nExporting datasets...')                                                  
    result_df.to_excel('./output/Commodity.xlsx', index=False)
    print('------------------------')
    print('Commodity.xlsx exported.')
else:
    print("Failed to fetch the webpage.")


# In[ ]:





# In[ ]:




