import re
from datetime import datetime

import pandas as pd
import time
import logging
from RPA.Browser.Selenium import Selenium
from bs4 import BeautifulSoup

from src.utils.logger import create_logger

logger = logging.getLogger(__name__)
lib = Selenium()

# url = "https://casper-maringe.vercel.app"

url = "https://www.latimes.com"
search_phrase_element = "data-element='search-button'"
search_input_element = "data-element='search-form-input'"
search_button_element = "data-element='search-submit-button'"
articles_list_element = "search-results-module-results-menu"

# url = "https://www.reuters.com/"
# search_phrase_element = "data-testid='Button'"
# search_input_element = "data-testid='FormField:input'"
# search_button_element = "data-testid='Button'"

search_phrase = "how to cook"


def extract_money(text):
    # Regular expression to find money values
    money_pattern = r"\$[\d,.]+|\b\d+\s(?:dollars|USD)\b"

    # Check if text is a string
    if isinstance(text, str):
        return bool(re.search(money_pattern, text))
    else:
        return False


def get_element_text_safe(article_element, selector):
    try:
        element = article_element.find(class_=selector)
        return element.text if element else None
    except Exception as e:
        print(e)
        return None


def search_element(selector):
    return lib.find_element(selector)


def open_browser():
    print("Thread 1")
    lib.open_available_browser(url, headless=False)


def interact_with_page():
    print("Time caught here")

    lib.wait_until_element_is_visible(f"css:button[{search_phrase_element}]")
    search_button = search_element(f"css:button[{search_phrase_element}]")
    search_button.click()

    search_input = search_element(f"css:input[{search_input_element}]")
    time.sleep(2)
    search_input.send_keys(search_phrase)

    time.sleep(2)
    search_submit_button = search_element(f"css:button[{search_button_element}]")
    search_submit_button.click()

    lib.wait_until_location_is_not(url)
    current_url = lib.driver.current_url
    print(f"Current URL: {current_url}")

    # Find the select element
    select_element = lib.find_element("css:select.select-input")

    # Click the select element to open the dropdown
    select_element.click()

    # Wait for 2 seconds
    time.sleep(2)

    lib.driver.execute_script("arguments[0].value = '1';", select_element)

    # Trigger the change event to apply the selection
    lib.driver.execute_script("arguments[0].dispatchEvent(new Event('change', { bubbles: true }));", select_element)

    time.sleep(2)
    lib.wait_until_location_is_not(current_url)
    current_url = lib.driver.current_url
    print(f"Current URL: {current_url}")

    # Find the parent element containing all articles
    lib.wait_until_element_is_visible(f"css:ul.{articles_list_element}")
    articles_parent = search_element(f"css:ul.{articles_list_element}")

    # Find all li elements directly under articles_parent
    all_li_elements = articles_parent.find_elements(by='tag name', value='li')

    print(all_li_elements)

    articles_data = []

    # Iterate through each article
    for article in all_li_elements:
        article_html = article.get_attribute("outerHTML")
        article_element = BeautifulSoup(article_html, 'html.parser')
        print(article_element)

        # Extracting title
        title_element = article_element.find(class_='promo-title')
        print(title_element.text)
        # print(article.find_element("h3", {"class": "promo-title"}).text)

        title = get_element_text_safe(article_element, "promo-title")
        date = get_element_text_safe(article_element, "promo-timestamp")
        description = get_element_text_safe(article_element, "promo-description")

        print(title, date, description)

        img_element = article_element.find('img', class_='image')
        if img_element:
            image_src = img_element['src']
            print(f"Image source: {image_src}")
        else:
            print("Image source not found.")

        # image_element = article.find_element(".image") if article.find_elements(".image") else None
        # image_url = image_element.get_attribute("src") if image_element else None

        # Count of search phrases in the title and description
        title_count = title.lower().count(search_phrase.lower()) if title else 0
        description_count = description.lower().count(search_phrase.lower()) if description else 0

        # Check for money in title or description
        contains_money = extract_money(title) or extract_money(description) if title or description else False

        article_data = {
            "title": title,
            "date": date,
            "description": description,
            # "picture_filename": image_url.split("/")[-1] if image_url else None,
            "title_description_search_count": title_count + description_count,
            "contains_money": contains_money
        }

        articles_data.append(article_data)

    # Convert to DataFrame
    df = pd.DataFrame(articles_data)
    current_datetime = datetime.now().strftime("%Y%m%d%H%M%S")

    filename = f"./files/excel/data_{current_datetime}.xlsx"

    # Save DataFrame to Excel with the constructed filename
    df.to_excel(filename, index=False)

    print("Data saved to search_results.xlsx")

    time.sleep(30000)

    lib.close_browser()


def web_scrapping():
    open_browser()
    interact_with_page()

    time.sleep(30000)
    lib.close_browser()


def main():
    create_logger(__name__)
    web_scrapping()
    logger.info('Finished Rpa Challenge process...')


if __name__ == '__main__':
    main()
