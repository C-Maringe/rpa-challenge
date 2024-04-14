import os
import re
from datetime import datetime

import pandas as pd
import time
import logging

import requests
from RPA.Browser.Selenium import Selenium
from bs4 import BeautifulSoup

from src.utils.date_validator import is_valid_date_format, get_current_date_if_ago, filter_articles_by_month
from src.utils.logger import create_logger

logger = logging.getLogger(__name__)
lib = Selenium()

# url = "https://casper-maringe.vercel.app"

url = "https://www.latimes.com"
search_phrase_element = "data-element='search-button'"
search_input_element = "data-element='search-form-input'"
search_button_element = "data-element='search-submit-button'"
articles_list_element = "search-results-module-results-menu"
next_page_element = "search-results-module-next-page"
topics_list_element = "data-name='Topics'"

search_phrase = "trump"
categories = {
    'sports': ['sports', 'football', 'basketball', 'baseball', 'tennis'],
    'politics': ['politics', 'election', 'president', 'government', 'congress'],
    'food': ['food', 'cooking', 'recipe', 'restaurant', 'chef'],
    'entertainment': ['entertainment', 'movie', 'music', 'celebrity', 'tv show'],
    'technology': ['technology', 'tech', 'innovation', 'software', 'gadget'],
    'health': ['health', 'wellness', 'medical', 'fitness'],
    'business': ['business', 'economy', 'finance', 'market'],
    'environment': ['environment', 'climate', 'sustainability', 'green']
}
topic = "sports"
months = 5
valid_months = filter_articles_by_month(months)
keep_going_to_next_page = True


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


def search_phrase_handler():
    lib.wait_until_element_is_visible(f"css:button[{search_phrase_element}]")
    search_button = search_element(f"css:button[{search_phrase_element}]")
    search_button.click()

    search_input = search_element(f"css:input[{search_input_element}]")
    time.sleep(2)
    search_input.send_keys(search_phrase)

    time.sleep(2)
    search_submit_button = search_element(f"css:button[{search_button_element}]")
    search_submit_button.click()

    time.sleep(2)


def apply_topic_filters(all_topic_elements, category_keywords):
    """Apply filters based on the category keywords."""
    for topic_element in all_topic_elements:
        try:
            topic_html = topic_element.get_attribute("outerHTML")
            topic_element_parser = BeautifulSoup(topic_html, 'html.parser')
            topic_name_element = topic_element_parser.find("span")
            topic_name = ""

            if topic_name_element:
                topic_name = topic_name_element.text.lower()
                print(topic_name)
            else:
                print("No <span> element found")

            if topic_name != "":
                for keyword in category_keywords:
                    if keyword in topic_name:
                        try:
                            checkbox_input = topic_element.find_element(by='tag name', value='input')
                            checkbox_value = checkbox_input.get_attribute("value")
                            if checkbox_input.is_selected():
                                print("Checkbox is currently checked.")
                            else:
                                print("Checkbox is not currently checked.")
                                lib.driver.execute_script(f"""
                                        var checkbox = document.querySelector("input[value='{checkbox_value}']");
                                        if (checkbox) {{
                                            if (!checkbox.checked) {{
                                                checkbox.click();
                                            }}
                                        }}
                                    """)
                        except Exception as e:
                            print("No input element found within topic_element.")
                        # break
        except Exception as e:
            # print(e)
            print("Something went wrong here, but relax its not a bigger deal")


def filter_by_category():
    """Filter news based on categories."""
    lib.wait_until_element_is_visible(f"css:ul[{topics_list_element}]")
    topic_container_element = lib.find_element(f"css:ul[{topics_list_element}]")
    all_topic_elements = topic_container_element.find_elements(by='tag name', value='li')

    if topic in categories:
        category_keywords = categories[topic]
        apply_topic_filters(all_topic_elements, category_keywords)
        time.sleep(2)
    else:
        print("No valid topic to filter with")


def sort_by_newest():
    lib.wait_until_location_is_not(url)

    # Find the select element
    lib.wait_until_element_is_visible("css:select.select-input")
    select_element = lib.find_element("css:select.select-input")

    # Click the select element to open the dropdown
    select_element.click()

    # Wait for 2 seconds
    time.sleep(2)

    lib.driver.execute_script("arguments[0].value = '1';", select_element)

    # Trigger the change event to apply the selection
    lib.driver.execute_script("arguments[0].dispatchEvent(new Event('change', { bubbles: true }));", select_element)

    time.sleep(2)


def next_page():
    lib.wait_until_element_is_visible(f"css:.{next_page_element}")
    next_month = lib.find_element(f"css:.{next_page_element}")
    next_month.click()
    time.sleep(2)


def get_articles():
    global keep_going_to_next_page
    # Find the parent element containing all articles
    time.sleep(2)
    lib.wait_until_element_is_visible(f"css:ul.{articles_list_element}")
    articles_parent = search_element(f"css:ul.{articles_list_element}")

    # Find all li elements directly under articles_parent
    all_li_elements = articles_parent.find_elements(by='tag name', value='li')

    articles_data = []

    # Iterate through each article
    for article in all_li_elements:
        article_html = article.get_attribute("outerHTML")
        article_element = BeautifulSoup(article_html, 'html.parser')

        title = get_element_text_safe(article_element, "promo-title")
        date = get_element_text_safe(article_element, "promo-timestamp")
        description = get_element_text_safe(article_element, "promo-description")

        formatted_date = get_current_date_if_ago(date)

        if not is_valid_date_format(formatted_date, valid_months):
            print(f"Skipping article '{title}' with date '{formatted_date}' as it's not within the valid months.")
            keep_going_to_next_page = False
            return articles_data

        print(title, formatted_date, description)
        picture_filename = ""

        img_element = article_element.find('img', class_='image')
        if img_element:
            image_src = img_element['src']
            print(f"Image source: {image_src}")
            response = requests.get(image_src)
            if response.status_code == 200:
                directory_path = "./files/images"

                # Create the directory if it doesn't exist
                if not os.path.exists(directory_path):
                    os.makedirs(directory_path)

                # Extract filename from image_src
                filename = image_src.split("/")[-1]
                filename_parts = filename.split("%2F")
                if len(filename_parts) > 1:
                    filename = filename_parts[-1]
                if not any(filename.lower().endswith(ext) for ext in ['.jpg', '.jpeg', '.png', '.gif']):
                    filename += '.jpg'
                filepath = os.path.join(directory_path, filename)

                # Save the image to the src/files/images directory
                with open(filepath, 'wb') as f:
                    f.write(response.content)

                # Update the article_data with the image filename
                picture_filename = filename
                print(f"Image saved as {filename}")
            else:
                print("Failed to download image.")
        else:
            print("Image source not found.")

        # Count of search phrases in the title and description
        title_count = title.lower().count(search_phrase.lower()) if title else 0
        description_count = description.lower().count(search_phrase.lower()) if description else 0

        # Check for money in title or description
        contains_money = extract_money(title) or extract_money(description) if title or description else False

        article_data = {
            "title": title,
            "date": formatted_date,
            "description": description,
            "picture_filename": picture_filename,
            "title_description_search_count": title_count + description_count,
            "contains_money": contains_money
        }

        articles_data.append(article_data)

    return articles_data


def save_articles(combined_articles_data):
    # Convert to DataFrame
    df = pd.DataFrame(combined_articles_data)
    current_datetime = datetime.now().strftime("%Y%m%d%H%M%S")

    filename = f"./files/excel/data_{current_datetime}.xlsx"

    # Save DataFrame to Excel with the constructed filename
    df.to_excel(filename, index=False)

    print("Data saved to search_results.xlsx")


def web_scrapping():
    open_browser()

    search_phrase_handler()
    sort_by_newest()
    filter_by_category()
    combined_articles_data = []
    if months < 0:
        print("No data for the selected period")
    else:
        number_of_months = months + 1 if months == 0 else months
        # print(number_of_months)
        # for month in range(0, number_of_months):
        #     articles_data_returned = get_articles()
        #     combined_articles_data.extend(articles_data_returned)
        #     if months != month:
        #         next_page()
        while keep_going_to_next_page:
            articles_data_returned = get_articles()
            combined_articles_data.extend(articles_data_returned)
            print(keep_going_to_next_page)
            if keep_going_to_next_page:
                next_page()

    save_articles(combined_articles_data)

    time.sleep(30000)
    lib.close_browser()


def main():
    create_logger(__name__)
    web_scrapping()
    logger.info('Finished Rpa Challenge process...')


if __name__ == '__main__':
    main()
