import calendar
from datetime import datetime
import re


def filter_articles_by_month(months):
    months = 1 if months <= 0 else months
    try:
        current_month = datetime.now().month
        current_year = datetime.now().year

        # Convert month number to month name and slice to get abbreviation
        month_name = calendar.month_name[current_month][:3].lower()

        print("Current month:", month_name)
        print("Current year:", current_year)

        # Create a list to store valid months
        valid_months = []

        for i in range(months):
            month = current_month - i
            year = current_year

            if month <= 0:
                month += 12
                year -= 1

            valid_months.append((month, year))

        return valid_months
    except Exception as e:
        print(f"Error in filter_articles_by_month: {e}")
        return []


def is_valid_date_format(date_str, valid_months):
    try:
        # Convert date string to lowercase
        date_str = date_str.lower()

        # Check if the date string contains "ago"
        if "ago" in date_str:
            # Return True as it's considered valid for our purpose
            return True

        # Define the regular expression pattern for the date format
        pattern = r'\b(?:january|february|march|april|may|june|july|august|september|october|november|december)\s+\d{1,2},\s+\d{4}\b'
        pattern_short = r'\b(?:jan\.|feb\.|mar\.|apr\.|may\.|jun\.|jul\.|aug\.|sep\.|oct\.|nov\.|dec\.)\s+\d{1,2},\s+\d{4}\b'

        # Check if the date string matches the patterns
        if bool(re.match(pattern, date_str) or re.match(pattern_short, date_str)):
            # Extract month and year from the date string
            month_name, day, year = date_str.split()
            month_name = month_name.rstrip(',').lower()[:3]

            month_number = None
            for i, month in enumerate(calendar.month_abbr):
                if month_name == month.lower():
                    month_number = i
                    break

            if month_number is not None:
                year = int(year)
                if (month_number, year) in valid_months:
                    return True

        return False
    except Exception as e:
        print(f"Error in is_valid_date_format: {e}")
        return False


def get_current_date_if_ago(date_str):
    try:
        if "ago" in date_str.lower():
            return datetime.now().strftime("%B %d, %Y")
        return date_str
    except Exception as e:
        print(f"Error in get_current_date_if_ago: {e}")
        return date_str