
def active_companies():

    import time
    import os
    import pandas as pd
    from io import StringIO
    from selenium import webdriver
    from selenium.webdriver.chrome.options import Options
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
    from selenium.webdriver.common.by import By
    import datetime
        # Set the URL and output file path
    base_url = "https://nepalstock.com/company"
        
        # Set up Selenium WebDriver with Chrome options
    options = Options()
    options.headless = True  # Enable headless mode
    driver = webdriver.Chrome(options=options)

    
    # Open the webpage
    driver.get(base_url)
    
    # Wait for the dropdown to be present
    wait = WebDriverWait(driver, 10)
    dropdown = wait.until(EC.presence_of_element_located((By.XPATH, "/html/body/app-root/div/main/div/app-company/div/div[2]/div/div[5]/div/select")))
    
    # Click the dropdown to reveal options
    dropdown.click()
    
    # Select '500' from the dropdown using the specific XPath
    option_500 = wait.until(EC.presence_of_element_located((By.XPATH, "/html/body/app-root/div/main/div/app-company/div/div[2]/div/div[5]/div/select/option[6]")))
    option_500.click()
    
    # Wait for the table to reload with 500 rows
    wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "table.table__lg.table-striped.table__border.table__border--bottom")))
    
    # Extract the table HTML
    table_html = driver.find_element(By.CSS_SELECTOR, "table.table__lg.table-striped.table__border.table__border--bottom").get_attribute("outerHTML")
    
    # Use Pandas to read the HTML table
    active_companies_df = pd.read_html(StringIO(table_html))[0]
    
    # Save the DataFrame to a CSV file
    
    # Close the WebDriver
    driver.quit()


# Define the data
    data = {'SN': list(range(1, 15)),
    'Name': [
        'Banking SubIndex', 'Development Bank Index', 'Finance Index', 
        'Hotels And Tourism', 'HydroPower Index', 'Investment', 
        'Life Insurance', 'Manufacturing And Processing', 'Microfinance Index', 
        'Mutual Fund', 'Non Life Insurance', 'Others Index', 
        'Trading Index', 'Nepse Index'
    ],
    'Symbol': [
        'Banking SubIndex', 'Development Bank Index', 'Finance Index', 
        'Hotels And Tourism', 'HydroPower Index', 'Investment', 
        'Life Insurance', 'Manufacturing And Processing', 'Microfinance Index', 
        'Mutual Fund', 'Non Life Insurance', 'Others Index', 
        'Trading Index', 'Nepse Index'
    ],
    'Status': [
        'Active', 'Active', 'Active', 
        'Active', 'Active', 'Active', 
        'Active', 'Active', 'Active', 
        'Active', 'Active', 'Active', 
        'Active', 'Active'
    ],
    'Sector': [
        'Index', 'Index', 'Index', 
        'Index', 'Index', 'Index', 
        'Index', 'Index', 'Index', 
        'Index', 'Index', 'Index', 
        'Index', 'Index'
    ],
    'Instrument': [
        'Index', 'Index', 'Index', 
        'Index', 'Index', 'Index', 
        'Index', 'Index', 'Index', 
        'Index', 'Index', 'Index', 
        'Index', 'Index'
    ]
}

    # Create the DataFrame
    indices_df = pd.DataFrame(data)
    index_and_stock_df = pd.concat([active_companies_df,indices_df ], ignore_index=True)
    index_and_stock_df.to_csv(r"C:\Users\Dell\Python Projects\Price Adjustments Program\ActiveCompanies.csv", index=False)
    return index_and_stock_df
    