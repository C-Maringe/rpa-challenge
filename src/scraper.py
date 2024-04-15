import os
import time
from datetime import datetime

import pandas as pd
import requests
import re
from bs4 import BeautifulSoup

from src.utils.logger import create_logger
from src.utils.date_validator import is_valid_date_format, get_current_date_if_ago, filter_articles_by_month
from src.browser_manager import BrowserManager

logger = create_logger(__name__)


def extract_money(text):
    money_pattern = r"\$[\d,.]+|\b\d+\s(?:dollars|USD)\b"
    return bool(re.search(money_pattern, text))


def get_element_text_safe(article_element, selector):
    try:
        element = article_element.find(class_=selector)
        return element.text if element else None
    except Exception as e:
        logger.error(e)
        return None


class Scraper:
    def __init__(self, url, search_phrase, topic, months, categories, current_dir):
        self.url = url
        self.current_dir = current_dir
        self.search_phrase = search_phrase
        self.topic = topic
        self.months = months
        self.valid_months = filter_articles_by_month(months)
        self.browser_manager = BrowserManager()
        logger.info("Scraping initiated successfully")
        self.keep_going_to_next_page = True
        self.articles = []
        self.categories = categories

    def search_phrase_handler(self):
        self.browser_manager.wait_until_element_is_visible("css:button[data-element='search-button']")
        search_button = self.browser_manager.find_element("css:button[data-element='search-button']")
        search_button.click()

        search_input = self.browser_manager.find_element("css:input[data-element='search-form-input']")
        time.sleep(2)
        search_input.send_keys(self.search_phrase)

        time.sleep(2)
        search_submit_button = self.browser_manager.find_element("css:button[data-element='search-submit-button']")
        search_submit_button.click()

        time.sleep(2)

    def apply_topic_filters(self, all_topic_elements, category_keywords):
        for topic_element in all_topic_elements:
            try:
                topic_html = topic_element.get_attribute("outerHTML")
                topic_element_parser = BeautifulSoup(topic_html, 'html.parser')
                topic_name_element = topic_element_parser.find("span")
                topic_name = ""

                if topic_name_element:
                    topic_name = topic_name_element.text.lower()
                    logger.info(topic_name)
                else:
                    logger.info("No <span> element found")

                if topic_name != "":
                    for keyword in category_keywords:
                        if keyword in topic_name:
                            try:
                                checkbox_input = topic_element.find_element(by='tag name', value='input')
                                checkbox_value = checkbox_input.get_attribute("value")
                                if checkbox_input.is_selected():
                                    logger.info("Checkbox is currently checked.")
                                else:
                                    logger.info("Checkbox is not currently checked.")
                                    self.browser_manager.lib.driver.execute_script(f"""
                                            var checkbox = document.querySelector("input[value='{checkbox_value}']");
                                            if (checkbox) {{
                                                if (!checkbox.checked) {{
                                                    checkbox.click();
                                                }}
                                            }}
                                        """)
                                time.sleep(1)
                            except Exception as e:
                                logger.error("No input element found within topic_element.")
            except Exception as e:
                if "stale" in str(e):
                    logger.error("Message: stale element reference: stale element not found in the current frame")
                    break  # Exit the loop
                else:
                    logger.error("Something went wrong here, but relax, it's not a bigger deal. It's just for "
                                 "demonstration purposes.")
                    break  # Exit the loop

    def filter_by_category(self):
        self.browser_manager.wait_until_element_is_visible("css:ul[data-name='Topics']")
        topic_container_element = self.browser_manager.find_element("css:ul[data-name='Topics']")
        all_topic_elements = topic_container_element.find_elements(by='tag name', value='li')

        if self.topic in self.categories:
            category_keywords = self.categories[self.topic]
            self.apply_topic_filters(all_topic_elements, category_keywords)
            time.sleep(2)
        else:
            logger.info("No valid topic to filter with")

    def sort_by_newest(self):
        self.browser_manager.wait_until_element_is_visible("css:select.select-input")
        select_element = self.browser_manager.find_element("css:select.select-input")

        select_element.click()
        time.sleep(2)
        self.browser_manager.lib.driver.execute_script("arguments[0].value = '1';", select_element)
        self.browser_manager.lib.driver.execute_script("arguments[0].dispatchEvent(new Event('change', { bubbles: "
                                                       "true }));", select_element)
        time.sleep(2)

    def next_page(self):
        self.browser_manager.wait_until_element_is_visible("css:.search-results-module-next-page")
        next_month = self.browser_manager.find_element("css:.search-results-module-next-page")
        next_month.click()
        time.sleep(2)

    def get_articles(self):
        articles_data = []
        self.browser_manager.wait_until_element_is_visible("css:.search-results-module-results-menu")
        articles_parent = self.browser_manager.find_element("css:.search-results-module-results-menu")
        all_li_elements = articles_parent.find_elements(by='tag name', value='li')

        for article in all_li_elements:
            article_html = article.get_attribute("outerHTML")
            article_element = BeautifulSoup(article_html, 'html.parser')

            title = get_element_text_safe(article_element, "promo-title")
            date = get_element_text_safe(article_element, "promo-timestamp")
            description = get_element_text_safe(article_element, "promo-description")

            formatted_date = get_current_date_if_ago(date)

            if not is_valid_date_format(formatted_date, self.valid_months):
                logger.info(f"Skipping article '{title}' with date '{formatted_date}' as it's not within the valid "
                            f"months.")
                self.keep_going_to_next_page = False
                return articles_data

            logger.info(f"{title}, {formatted_date}, {description}")
            picture_filename = ""

            img_element = article_element.find('img', class_='image')
            if img_element:
                image_src = img_element['src']
                logger.info(f"Image source: {image_src}")
                response = requests.get(image_src)
                if response.status_code == 200:
                    directory_path = os.path.join(self.current_dir, "output/files/images")
                    if not os.path.exists(directory_path):
                        os.makedirs(directory_path)

                    filename = image_src.split("/")[-1]
                    filename_parts = filename.split("%2F")
                    if len(filename_parts) > 1:
                        filename = filename_parts[-1]
                    if not any(filename.lower().endswith(ext) for ext in ['.jpg', '.jpeg', '.png', '.gif']):
                        filename += '.jpg'
                    filepath = os.path.join(directory_path, filename)

                    with open(filepath, 'wb') as f:
                        f.write(response.content)
                    picture_filename = filename
                    logger.info(f"Image saved as {filename}")
                else:
                    logger.error("Failed to download image.")
            else:
                logger.info("Image source not found.")

            title_count = title.lower().count(self.search_phrase.lower()) if title else 0
            description_count = description.lower().count(self.search_phrase.lower()) if description else 0
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

    def save_articles(self):
        df = pd.DataFrame(self.articles)
        current_datetime = datetime.now().strftime("%Y%m%d%H%M%S")
        directory_path = os.path.join(self.current_dir, "output/files/excel")

        if not os.path.exists(directory_path):
            os.makedirs(directory_path)

        filename = f"{directory_path}/data_{current_datetime}.xlsx"
        df.to_excel(filename, index=False)
        logger.info(f"Data saved to {filename}")

    def run(self):
        try:
            self.browser_manager.open_browser(self.url)
            self.search_phrase_handler()
            self.sort_by_newest()
            self.filter_by_category()

            while self.keep_going_to_next_page:
                self.articles.extend(self.get_articles())
                if self.keep_going_to_next_page:
                    self.next_page()

            self.save_articles()
            self.browser_manager.close_browser()
        except Exception as e:
            logger.error(f"Error in scraping: {e}")

