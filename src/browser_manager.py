from RPA.Browser.Selenium import Selenium


class BrowserManager:
    def __init__(self):
        self.lib = Selenium()


    def open_browser(self, url):
        self.lib.open_available_browser(url, headless=False)

    def close_browser(self):
        self.lib.close_browser()

    def find_element(self, selector):
        return self.lib.find_element(selector)

    def wait_until_element_is_visible(self, selector):
        self.lib.wait_until_element_is_visible(selector)
