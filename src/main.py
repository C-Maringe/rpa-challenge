import time
import logging
from RPA.Browser.Selenium import Selenium

from src.utils.logger import create_logger

logger = logging.getLogger(__name__)


def web_scrapping():
    # Initialize Selenium library
    lib = Selenium()

    # Open the browser and navigate to the specified URL
    lib.open_available_browser("https://google.com")

    # Wait for 10 seconds
    time.sleep(10)

    # Get the page source
    page_source = lib.get_source()

    # Print the page source
    print(page_source)

    # Close the browser window
    lib.close_browser()


def main():
    create_logger(__name__)
    web_scrapping()
    logger.info('Finished Rpa Challenge process...')


if __name__ == '__main__':
    main()
