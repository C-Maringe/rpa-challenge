# RPA Challenge Documentation

## Overview

This documentation provides an overview and details of a Robocorp RPA bot built using Python. The bot aims to scrape articles from the [Los Angeles Times](https://www.latimes.com) website based on specific topics and keywords, and then saves the data in an Excel file.

## Files Structure

- `tasks.py`: Entry point for Robocorp tasks.
- `src/main.py`: Main script to initiate the scraping process.
- `src/scraper.py`: Contains the Scraper class responsible for web scraping.
- `src/article.py`: Defines the Article class to store article details.
- `src/browser_manager.py`: Manages browser operations using Selenium.
- `src/utils/logger.py`: Handles logging functionalities.
- `src/utils/date_validator.py`: Provides date validation and filtering functionalities.
- `output/`: Folder containing logs, images, and Excel files.

## Running the Robot

#### VS Code
1. Get [Robocorp Code](https://robocorp.com/docs/developer-tools/visual-studio-code/extension-features) -extension for VS Code.
1. You'll get an easy-to-use side panel and powerful command-palette commands for running, debugging, code completion, docs, etc.

#### Command line

1. [Get RCC](https://github.com/robocorp/rcc?tab=readme-ov-file#getting-started)
1. Use the command: `rcc run`

## How to Run manually

To execute the bot, you can run the `rpa_challenge` task defined in `tasks.py` in visual studio.

## Results

🚀 After running the bot, check out the following directories in the `output` folder:

- **Excel Files**: `output/files/excel` - Contains the Excel files with scraped article data.
- **Images**: `output/files/images` - Contains the images downloaded from the articles.

🚀 After running the bot, check out the `log.html` under the `output` -folder.

## Main.py

### Function: main()

- **Purpose**: Initiates the RPA Challenge by setting up the logging, defining scraping parameters, and running the Scraper.

#### Parameters

- `url`: Target URL (https://www.latimes.com)
- `search_phrase`: Keyword to search for (e.g., "trump")
- `topic`: Topic/category for filtering articles (e.g., "sports")
- `months`: Number of past months to consider (e.g., 6)
- `categories`: Dictionary of categories and their associated keywords

#### Steps

1. **Initialize logger**: Sets up logging for the script.
2. **Define scraping parameters**: Defines the URL, search phrase, topic, months, and categories.
3. **Instantiate Scraper**: Creates a Scraper object with the defined parameters.
4. **Run Scraper**: Calls the `run()` method of the Scraper object to start the scraping process.

## Scraper.py

### Class: Scraper

- **Purpose**: Handles web scraping functionalities.

#### Attributes

- `url`: Target URL
- `search_phrase`: Keyword to search for
- `topic`: Topic/category for filtering articles
- `months`: Number of past months to consider
- `valid_months`: List of valid months for filtering
- `browser_manager`: BrowserManager object
- `keep_going_to_next_page`: Flag to control pagination
- `articles`: List to store scraped articles
- `categories`: Dictionary of categories and their associated keywords

#### Methods

- `search_phrase_handler()`: Handles the search functionality on the website.
- `apply_topic_filters(all_topic_elements, category_keywords)`: Applies topic filters based on category keywords.
- `filter_by_category()`: Filters articles based on the selected topic.
- `sort_by_newest()`: Sorts articles by newest.
- `next_page()`: Navigates to the next page of search results.
- `get_articles()`: Scrapes article details from the current page.
- `save_articles()`: Saves scraped articles to an Excel file.
- `run()`: Main method to run the scraping process.

## Article.py

### Class: Article

- **Purpose**: Represents an article object with its details.

#### Attributes

- `title`: Article title
- `date`: Article publication date
- `description`: Article description
- `picture_filename`: Filename of the article image
- `title_description_search_count`: Count of search keyword occurrences in title and description
- `contains_money`: Flag indicating if the article mentions money

## Browser_manager.py

### Class: BrowserManager

- **Purpose**: Manages browser operations using Selenium.

#### Methods

- `open_browser(url)`: Opens a browser with the specified URL.
- `close_browser()`: Closes the browser.
- `find_element(selector)`: Finds and returns a web element using the provided selector.
- `wait_until_element_is_visible(selector)`: Waits until the specified element is visible.

## Utils

### Logger.py

- **Purpose**: Provides logging functionalities.

### Date_validator.py

- **Purpose**: Provides date validation and filtering functionalities.

## Dependencies

- `robocorp.tasks`: For task definitions.
- `pandas`: For data manipulation and Excel file handling.
- `requests`: For making HTTP requests.
- `beautifulsoup4`: For parsing HTML content.
- `selenium`: For browser automation.
- `logging`: For logging functionalities.

## Conclusion

This bot demonstrates the use of Robocorp, Python, and Selenium for web scraping tasks. It scrapes articles from the Los Angeles Times website based on specific topics and keywords, filters and sorts them, and saves the data in an Excel file.
