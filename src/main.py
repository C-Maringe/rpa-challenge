import os

from robocorp import vault
from robocorp import workitems

from src.scraper import Scraper
from src.utils.logger import create_logger


def main(current_dir):
    secrets = {}
    logger = create_logger(__name__)
    logger.info("Starting the RPA Challenge...")
    logger.info(current_dir)
    logger.info(secrets)
    item = workitems.inputs.current
    logger.info(f"Received payload: {item.payload}")

    # Extract values from the payload with default values
    search_phrase = item.payload.get("search_phrase", "trump")
    topic = item.payload.get("topic", "football")
    months = int(item.payload.get("months", 4))
    logger.info(f"Received payload: {search_phrase, topic, months}")
    try:
        secrets = vault.get_secret("RpaChallenge")
        logger.info(secrets)
        logger.info(secrets["search_phrase"])
        logger.info(secrets["months"])
        logger.info(secrets["topic"])
    except Exception as e:
        logger.info(str(e))

    url = "https://www.latimes.com"
    # search_phrase = secrets["search_phrase"] if secrets else "Weather"
    # topic = secrets["topic"] if secrets else "sports"
    # months = int(secrets["months"]) if secrets else 1

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

    scraper = Scraper(
        url,
        search_phrase,
        topic,
        months,
        categories,
        current_dir)
    scraper.run()
    logger.info("RPA Challenge ended...")


if __name__ == "__main__":
    current_dir = os.path.dirname(__file__)
    main(current_dir)
