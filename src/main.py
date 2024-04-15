from src.scraper import Scraper
from src.utils.logger import create_logger


def main():
    logger = create_logger(__name__)
    logger.info("Starting the RPA Challenge...")
    url = "https://www.latimes.com"
    search_phrase = "trump"
    topic = "sports"
    months = 6
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

    scraper = Scraper(url, search_phrase, topic, months, categories)
    scraper.run()
    logger.info("RPA Challenge ended...")


if __name__ == "__main__":
    main()
