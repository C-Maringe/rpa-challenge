import os
import re
import time
from datetime import datetime
import pandas as pd
import requests
from bs4 import BeautifulSoup
from RPA.Browser.Selenium import Selenium

from src.utils.date_validator import is_valid_date_format, get_current_date_if_ago, filter_articles_by_month
from src.utils.logger import create_logger


def extract_money(text):
    money_pattern = r"\$[\d,.]+|\b\d+\s(?:dollars|USD)\b"
    return bool(re.search(money_pattern, text)) if isinstance(text, str) else False


class NewsScraper:
    def __init__(self):
        self.logger = create_logger(__name__)
        self.logger.info("Starting News Scraper...")
        self.lib = Selenium()
        self.keep_going_to_next_page = True
        self.search_phrase = "trump"
        self.categories = {
            'sports': ['sports', 'football', 'basketball', 'baseball', 'tennis'],
            'politics': ['politics', 'election', 'president', 'government', 'congress'],
            'food': ['food', 'cooking', 'recipe', 'restaurant', 'chef'],
            'entertainment': ['entertainment', 'movie', 'music', 'celebrity', 'tv show'],
            'technology': ['technology', 'tech', 'innovation', 'software', 'gadget'],
            'health': ['health', 'wellness', 'medical', 'fitness'],
            'business': ['business', 'economy', 'finance', 'market'],
            'environment': ['environment', 'climate', 'sustainability', 'green']
        }
        self.topic = "sports"
        self.months = 1
        self.valid_months = filter_articles_by_month(self.months)
        self.search_phrase_element = "data-element='search-button'"
        self.search_input_element = "data-element='search-form-input'"
        self.search_button_element = "data-element='search-submit-button'"
        self.articles_list_element = "search-results-module-results-menu"
        self.next_page_element = "search-results-module-next-page"
        self.topics_list_element = "data-name='Topics'"

    def get_element_text_safe(self, article_element, selector):
        try:
            element = article_element.find(class_=selector)
            return element.text if element else None
        except Exception as e:
            self.logger.error(f"Error getting text from element: {e}")
            return None

    def search_element(self, selector):
        return self.lib.find_element(selector)

    def open_browser(self):
        self.logger.info("Opening browser...")
        self.lib.open_available_browser("https://www.latimes.com", headless=False)

    def search_phrase_handler(self):
        try:
            self.logger.info("Handling search phrase...")
            self.lib.wait_until_element_is_visible(f"css:button[{self.search_phrase_element}]")
            search_button = self.search_element(f"css:button[{self.search_phrase_element}]")
            search_button.click()
            search_input = self.search_element(f"css:input[{self.search_input_element}]")
            time.sleep(2)
            search_input.send_keys(self.search_phrase)
            time.sleep(2)
            search_submit_button = self.search_element(f"css:button[{self.search_button_element}]")
            search_submit_button.click()
            time.sleep(2)
        except Exception as e:
            self.logger.error(f"Error handling search phrase: {e}")

    def apply_topic_filters(self, all_topic_elements, category_keywords):
        try:
            self.logger.info("Applying topic filters...")
            for topic_element in all_topic_elements:
                topic_html = topic_element.get_attribute("outerHTML")
                topic_element_parser = BeautifulSoup(topic_html, 'html.parser')
                topic_name_element = topic_element_parser.find("span")
                topic_name = topic_name_element.text.lower() if topic_name_element else ""

                if topic_name:
                    for keyword in category_keywords:
                        if keyword in topic_name:
                            try:
                                checkbox_input = topic_element.find_element(by='tag name', value='input')
                                checkbox_value = checkbox_input.get_attribute("value")
                                if not checkbox_input.is_selected():
                                    self.lib.driver.execute_script(f"""
                                        var checkbox = document.querySelector("input[value='{checkbox_value}']");
                                        if (checkbox && !checkbox.checked) {{
                                            checkbox.click();
                                        }}
                                    """)
                                time.sleep(1)
                            except Exception as e:
                                self.logger.error(
                                    "Error applying topic filters: No input element found within topic_element.")
        except Exception as e:
            self.logger.error("Error applying topic filters: ", exc_info=True)

    def filter_by_category(self):
        """Filter news based on categories."""
        self.lib.wait_until_element_is_visible(f"css:ul[{self.topics_list_element}]")
        topic_container_element = self.lib.find_element(f"css:ul[{self.topics_list_element}]")
        all_topic_elements = topic_container_element.find_elements(by='tag name', value='li')

        if self.topic in self.categories:
            category_keywords = self.categories[self.topic]
            self.apply_topic_filters(all_topic_elements, category_keywords)
            time.sleep(2)
        else:
            print("No valid topic to filter with")

    def sort_by_newest(self):
        try:
            self.logger.info("Sorting by newest...")
            self.lib.wait_until_location_is_not("https://www.latimes.com")
            self.lib.wait_until_element_is_visible("css:select.select-input")
            select_element = self.lib.find_element("css:select.select-input")
            select_element.click()
            time.sleep(2)
            self.lib.driver.execute_script("arguments[0].value = '1';", select_element)
            self.lib.driver.execute_script("arguments[0].dispatchEvent(new Event('change', { bubbles: true }));",
                                           select_element)
            time.sleep(2)
        except Exception as e:
            self.logger.error(f"Error sorting by newest: {e}")

    def next_page(self):
        try:
            self.logger.info("Navigating to next page...")
            self.lib.wait_until_element_is_visible(f"css:.{self.next_page_element}")
            next_month = self.lib.find_element(f"css:.{self.next_page_element}")
            next_month.click()
            time.sleep(2)
        except Exception as e:
            self.logger.error(f"Error navigating to next page: {e}")

    def get_articles(self):
        try:
            self.logger.info("Getting articles...")
            self.lib.wait_until_element_is_visible(f"css:ul.{self.articles_list_element}")
            articles_parent = self.search_element(f"css:ul.{self.articles_list_element}")
            all_li_elements = articles_parent.find_elements(by='tag name', value='li')

            articles_data = []
            for article in all_li_elements:
                article_html = article.get_attribute("outerHTML")
                article_element = BeautifulSoup(article_html, 'html.parser')
                title = self.get_element_text_safe(article_element, "promo-title")
                date = self.get_element_text_safe(article_element, "promo-timestamp")
                description = self.get_element_text_safe(article_element, "promo-description")
                formatted_date = get_current_date_if_ago(date)

                if not is_valid_date_format(formatted_date, self.valid_months):
                    self.logger.info(
                        f"Skipping article '{title}' with date '{formatted_date}' as it's not within the valid months.")
                    self.keep_going_to_next_page = False
                    return articles_data

                picture_filename = ""
                img_element = article_element.find('img', class_='image')
                if img_element:
                    image_src = img_element['src']
                    response = requests.get(image_src)
                    if response.status_code == 200:
                        directory_path = "./files/images"
                        if not os.path.exists(directory_path):
                            os.makedirs(directory_path)
                        filename = image_src.split("/")[-1].split("%2F")[-1] + '.jpg'
                        filepath = os.path.join(directory_path, filename)
                        with open(filepath, 'wb') as f:
                            f.write(response.content)
                        picture_filename = filename
                    else:
                        self.logger.error("Failed to download image.")

                title_count = title.lower().count(self.search_phrase.lower()) if title else 0
                description_count = description.lower().count(self.search_phrase.lower()) if description else 0
                contains_money = extract_money(title) or extract_money(description)

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
        except Exception as e:
            self.logger.error(f"Error getting articles: {e}")
            return []

    def save_articles(self, combined_articles_data):
        try:
            self.logger.info("Saving articles...")
            df = pd.DataFrame(combined_articles_data)
            current_datetime = datetime.now().strftime("%Y%m%d%H%M%S")
            filename = f"./files/excel/data_{current_datetime}.xlsx"
            df.to_excel(filename, index=False)
            self.logger.info(f"Data saved to {filename}")
        except Exception as e:
            self.logger.error(f"Error saving articles: {e}")

    def main(self):
        try:
            self.open_browser()
            self.search_phrase_handler()
            self.sort_by_newest()
            self.filter_by_category()
            combined_articles_data = []

            while self.keep_going_to_next_page:
                articles_data_returned = self.get_articles()
                combined_articles_data.extend(articles_data_returned)
                if self.keep_going_to_next_page:
                    self.next_page()

            self.save_articles(combined_articles_data)
            time.sleep(5)
            self.lib.close_browser()
            self.logger.info('Finished Rpa Challenge process...')
        except Exception as e:
            self.logger.error(f"Main function error: {e}", exc_info=True)


if __name__ == '__main__':
    news_scraper = NewsScraper()
    news_scraper.main()
