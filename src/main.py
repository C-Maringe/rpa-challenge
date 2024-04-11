import time
import logging
from RPA.Browser.Selenium import Selenium

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
    logging.basicConfig(filename='myapp.log', level=logging.INFO)
    logger.info('Started')
    web_scrapping()
    logger.info('Finished')


if __name__ == '__main__':
    main()
