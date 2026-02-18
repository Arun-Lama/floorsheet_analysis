import time
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC


def free_float_market_cap():
    options = Options()
    options.add_argument("--headless=new")  # Use newer headless mode
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    options.add_argument("--window-size=1920,1080")
    options.add_argument(
        "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
    )

    driver = webdriver.Chrome(options=options)
    wait = WebDriverWait(driver, 10)

    try:
        driver.get("https://nepsealpha.com/traded-stocks")

        wait.until(EC.element_to_be_clickable((By.ID, "searchBtn"))).click()

        # --- Select 100 rows per page ---
        select_element = Select(driver.find_element(By.NAME, "DataTables_Table_0_length"))
        select_element.select_by_value("100")

        all_data = []

        while True:
            # Wait until table rows are present
            table = wait.until(EC.presence_of_element_located((By.ID, "DataTables_Table_0")))
            rows = table.find_elements(By.TAG_NAME, "tr")

            # Get headers from the first page only
            if not all_data:
                headers = [th.text.strip() for th in rows[0].find_elements(By.TAG_NAME, "th")]

            # Read all data rows from current page
            for row in rows[1:]:
                cols = row.find_elements(By.TAG_NAME, "td")
                if cols:
                    all_data.append([td.text.strip() for td in cols])

            # Try clicking next button
            try:
                next_btn = driver.find_element(By.CSS_SELECTOR, ".paginate_button.next")
                is_disabled = "disabled" in next_btn.get_attribute("class")
                if is_disabled:
                    break
                next_btn.click()
            except Exception:
                break

        df = pd.DataFrame(all_data, columns=headers)
        # Remove commas from all string values
        df = df.replace(',', '', regex=True)

        # Convert 'Floated Market Cap' to float
        df['Floated Market Cap'] = df['Floated Market Cap'].astype(float)
        df['Floated Shares'] = df['Floated Shares'].astype(float) 
        df = df[df["Floated Shares"].notna() & (df["Floated Shares"] != 0)]
        return df

    finally:
        driver.quit()
