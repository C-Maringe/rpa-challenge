from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

driver = webdriver.Chrome()
driver.get("https://www.herald.co.zw")
try:
    element = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.ID, "doc"))
    )
except Exception as e:
    print(e)
finally:
    driver.quit()