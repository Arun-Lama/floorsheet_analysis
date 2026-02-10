def get_total_tradedshares():
    import re
    from selenium import webdriver
    from selenium.webdriver.chrome.options import Options
    from selenium.webdriver.common.by import By
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC

    # Set up headless Chrome
    options = Options()
    # options.add_argument("--headless")
    driver = webdriver.Chrome(options=options)
    
    try:
        # Open the trading page
        driver.get("https://nepalstock.com.np")
    
        # Wait until the span with Total Traded Shares appears
        span = WebDriverWait(driver, 15).until(
            EC.presence_of_element_located((
                By.XPATH,
                "/html/body/app-root/div/main/div/app-dashboard/div[1]/div[1]/div/div[1]/div[2]/div[2]/span[2]"
            ))
        )
    
        # Extract the text, e.g., "Total Traded Shares | 18,496,138"
        text = span.text
    
        # Extract the number using regex
        match = re.search(r'([\d,]+)', text)
        if match:
            number_str = match.group(1).replace(",", "")
            volume = int(number_str)
            result = volume
        else:
            print("Volume value not found.")
            result = None
        return result
    finally:
        driver.quit()
    
    # If you're in a function, return `result` here.

