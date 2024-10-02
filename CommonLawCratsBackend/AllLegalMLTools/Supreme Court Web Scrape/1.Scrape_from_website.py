from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import os

os.makedirs('data', exist_ok=True)

driver = webdriver.Chrome()

def save_rows_to_files(rows, start_index):
    """Save each row as an HTML file starting from the given index."""
    for index, row in enumerate(rows, start=start_index):
        row_html = row.get_attribute('outerHTML')
        
        file_path = f"data/case_{index}.html"
        
        # Save the row HTML to the file
        with open(file_path, 'w', encoding='utf-8') as file:
            file.write(row_html)
    return start_index + len(rows)

try:
    base_url = "https://judgments.ecourts.gov.in/pdfsearch/index.php"
    driver.get(base_url)

    captcha_input = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.ID, "captcha"))
    )

    captcha_code = input("Please enter the CAPTCHA code: ")

    captcha_input.send_keys(captcha_code)

    search_button = driver.find_element(By.ID, "main_search")
    search_button.click()

    WebDriverWait(driver, 10).until(EC.url_changes(base_url))
    new_url = driver.current_url

    print(f"Redirected to: {new_url}")

    time.sleep(10)
    print("hit1")
    for i in range(178):
            next_button = driver.find_element(By.ID, "example_pdf_next")
            driver.execute_script("arguments[0].click();", next_button)
            time.sleep(2)

    case_index = 178001
    
    while True:
        
        rows = driver.find_elements(By.XPATH, "//tr[@role='row' and (contains(@class, 'odd') or contains(@class, 'even'))]")

        case_index = save_rows_to_files(rows, case_index)

        try:
            next_button = driver.find_element(By.ID, "example_pdf_next")
            next_button_class = next_button.get_attribute("class")
            
            if "paginate_button next disabled" in next_button_class:
                print("No more pages to navigate.")
                break
            
            driver.execute_script("arguments[0].click();", next_button)

            time.sleep(10)

        except Exception as e:
            print(f"Exception occurred while navigating to the next page: {e}")
            break

finally:
    driver.quit()
