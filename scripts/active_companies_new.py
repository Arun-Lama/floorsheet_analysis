import time
import os
import pandas as pd
from io import StringIO
from bs4 import BeautifulSoup

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import (
    TimeoutException,
    NoSuchElementException,
    ElementClickInterceptedException,
)
from webdriver_manager.chrome import ChromeDriverManager

import total_traded_shares

# ============================================================
# Setup Chrome
# ============================================================
HEADLESS = False

options = Options()
options.add_argument("start-maximized")
options.add_argument("--disable-gpu")
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")
options.add_argument("window-size=1920,1080")
options.add_argument("--remote-debugging-port=9222")

if HEADLESS:
    options.add_argument("--headless=new")

prefs = {"profile.managed_default_content_settings.images": 2}
options.add_experimental_option("prefs", prefs)

driver = webdriver.Chrome(
    service=Service(ChromeDriverManager().install()),
    options=options,
)

wait = WebDriverWait(driver, 20)
start_time = time.time()

# ============================================================
# Open Page
# ============================================================
driver.get("https://nepalstock.com/company")

# Wait for Angular app to stabilize
time.sleep(3)

# ============================================================
# Select "500" rows per page
# ============================================================
try:
    rows_dropdown_option = wait.until(
        EC.element_to_be_clickable(
            (
                By.XPATH,
                "//select/option[text()='500']"
            )
        )
    )
    rows_dropdown_option.click()
except TimeoutException:
    print("❌ Failed to select 500 rows")

# ============================================================
# Wait for table to reload
# ============================================================
wait.until(
    EC.presence_of_element_located(
        (By.CSS_SELECTOR, "table.table__lg.table-striped.table__border.table__border--bottom")
    )
)

# Small buffer for Angular DOM update
time.sleep(2)

# ============================================================
# Extract Table HTML
# ============================================================
table_element = driver.find_element(
    By.CSS_SELECTOR,
    "table.table__lg.table-striped.table__border.table__border--bottom"
)

table_html = table_element.get_attribute("outerHTML")

# ============================================================
# Convert to DataFrame
# ============================================================
active_companies_df = pd.read_html(StringIO(table_html))[0]

print(active_companies_df.head())
print(f"\nTotal rows: {len(active_companies_df)}")

# ============================================================
# Cleanup
# ============================================================
driver.quit()

print(f"\n⏱ Finished in {time.time() - start_time:.2f} seconds")
