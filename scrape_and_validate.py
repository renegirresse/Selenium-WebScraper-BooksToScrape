# Import necessary modules from Selenium
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.service import Service as FirefoxService
from selenium.webdriver.firefox.options import Options as FirefoxOptions
# For automatically managing the WebDriver executable
from webdriver_manager.firefox import GeckoDriverManager
# For pausing the script (useful for seeing actions during development)
import time
# For explicit waits (waiting for elements to be ready)
from selenium.webdriver.support.ui import WebDriverWait # Correctly imported
from selenium.webdriver.support import expected_conditions as EC
# For handling specific Selenium errors
from selenium.common.exceptions import NoSuchElementException, TimeoutException, StaleElementReferenceException
# For writing data to CSV files
import csv

# --- Start of the Test ---
print("Starting Web Scraping and Validation Test for Books to Scrape...")

# Initialize driver variable to None (good practice for cleanup)
driver = None
scraped_data = [] # This list will store dictionaries of scraped book info

try:
    # --- Browser Setup ---
    # Configure Firefox options (e.g., maximize window)
    firefox_options = FirefoxOptions()
    firefox_options.add_argument("--window-size=1920,1080")
    print("Firefox options configured.")

    # Set up the Firefox WebDriver using GeckoDriverManager
    # GeckoDriverManager automatically downloads/manages the correct GeckoDriver for Firefox
    service = FirefoxService(GeckoDriverManager().install())
    driver = webdriver.Firefox(service=service, options=firefox_options)

    # Navigate to the target website
    driver.get("http://books.toscrape.com/")
    driver.maximize_window() # Ensure window is maximized after navigation
    print("Browser (Firefox) opened and navigated to Books to Scrape.")
    time.sleep(2) # Give the page a moment to load visually

    # --- Scraping Logic with Pagination ---
    page_num = 1
    max_pages_to_scrape = 5 # Set to 5 for quicker demo/testing

    while True: # Loop indefinitely until we explicitly break out
        print(f"\n--- Scraping Page {page_num} ---")

        # --- Extract Category for the current page (from breadcrumbs) ---
        current_page_category = "N/A" # Default if not found
        try:
            # Find the breadcrumbs and then try to get the text of the last relevant li
            # This XPath targets the li right before the last one, which is usually the category if available
            category_element = WebDriverWait(driver, 5).until(
                EC.presence_of_element_located((By.XPATH, "//ul[@class='breadcrumb']/li[last()-1]/a"))
            )
            current_page_category = category_element.text.strip()
            print(f"Detected category for current page: '{current_page_category}'")
        except (NoSuchElementException, TimeoutException):
            # If on the home page or a page without a specific category in breadcrumbs,
            # it will likely show "Books" or "Home" as the last non-active item.
            # For the main page, we'll just note it as 'General' or 'Books'.
            # If it's the home page and breadcrumb is just "Home > Books", we'll default to "Books/General"
            if driver.current_url == "http://books.toscrape.com/":
                current_page_category = "Books/General"
            else:
                current_page_category = "N/A" # Fallback if a category isn't clear
            # print("Could not determine specific category from breadcrumbs for this page. Using 'Books/General' or 'N/A'.")


        try:
            # Explicitly wait up to 10 seconds for at least one book product to be visible on the page.
            # This ensures the page content has loaded before attempting to find elements.
            WebDriverWait(driver, 10).until( # <-- CORRECTED TYPO HERE: WebDriverWait
                EC.presence_of_element_located((By.CLASS_NAME, "product_pod"))
            )
        except TimeoutException:
            # If no product elements appear after 10 seconds, it's likely an empty or malformed page,
            # so we stop scraping.
            print(f"No products found on page {page_num}. Ending scraping.")
            break # Exit if no products are found after navigating to a new page

        # Find all elements that represent individual book containers on the current page.
        # Each book is typically wrapped in an <article> tag with the class "product_pod".
        book_elements = driver.find_elements(By.CLASS_NAME, "product_pod")
        print(f"Found {len(book_elements)} book elements on page {page_num}.")

        # Loop through each identified book container to extract its details.
        for i, book_element in enumerate(book_elements):
            title = "N/A"
            price = 0.0
            star_rating = "N/A"
            availability = "N/A"

            try:
                # Locate the title. It's usually within an <h3> tag, which contains an <a> tag.
                # We extract the 'title' attribute of the <a> tag for the full book title.
                title_element = book_element.find_element(By.TAG_NAME, "h3").find_element(By.TAG_NAME, "a")
                title = title_element.get_attribute("title").strip() # .strip() to remove leading/trailing whitespace

                # Locate the price. It's usually within a <p> tag with the class "price_color".
                price_element = book_element.find_element(By.CLASS_NAME, "price_color")
                price_str = price_element.text # Get the raw text, e.g., "£51.77"

                # Clean and convert the price string to a floating-point number.
                # Removes the currency symbol (£) and any leading/trailing whitespace.
                price = float(price_str.replace('£', '').strip())

                # Locate the star rating. It's within a <p> tag with a class like "star-rating One"
                rating_element = book_element.find_element(By.CSS_SELECTOR, "p.star-rating")
                # Get all classes, then find the rating word (One, Two, Three, Four, Five)
                rating_classes = rating_element.get_attribute("class").split()
                # The actual rating word is typically the second class
                star_rating = [c for c in rating_classes if c in ["One", "Two", "Three", "Four", "Five"]]
                star_rating = star_rating[0] if star_rating else "N/A"


                # Locate availability. It's within a <p> tag with class "instock availability".
                availability_element = book_element.find_element(By.CLASS_NAME, "instock")
                raw_availability_text = availability_element.text.strip()
                if "In stock" in raw_availability_text:
                     # Extract the number from "In stock (XX available)"
                     try:
                         # Use regex for more robust extraction, or simple split
                         import re
                         match = re.search(r'\((\d+) available\)', raw_availability_text)
                         if match:
                             availability = match.group(1) # Get the number
                         else:
                             availability = "Yes" # Just "In stock" without a count
                     except Exception:
                         availability = "Yes" # Fallback
                elif "Out of stock" in raw_availability_text:
                    availability = "0"
                else:
                    availability = raw_availability_text # Use raw text if format is unexpected


                # Store the extracted data
                scraped_data.append({
                    "title": title, 
                    "price": price,
                    "star_rating": star_rating,
                    "availability": availability,
                    "category": current_page_category # Add the category for the current page
                })
                # print(f"Scraped: Title='{title}', Price={price}, Rating='{star_rating}', Available='{availability}', Category='{current_page_category}'") 

            except NoSuchElementException as e:
                print(f"Warning: Missing element for book element {i+1} on page {page_num}: {e}. Skipping some data.")
                # Still append what we have, using N/A for missing fields
                scraped_data.append({
                    "title": title, 
                    "price": price,
                    "star_rating": star_rating,
                    "availability": availability,
                    "category": current_page_category
                })
            except ValueError:
                print(f"Warning: Could not convert price '{price_str}' to a number for book element {i+1} on page {page_num}. Skipping.")
                scraped_data.append({
                    "title": title, 
                    "price": 0.0, # Default to 0.0 if price conversion fails
                    "star_rating": star_rating,
                    "availability": availability,
                    "category": current_page_category
                })
            
        # --- Pagination Control ---
        # Check if we have already scraped the maximum desired number of pages.
        if page_num >= max_pages_to_scrape:
            print(f"Reached maximum page limit of {max_pages_to_scrape}. Stopping scraping.")
            break # Exit the while loop as the page limit is hit.

        try:
            # Attempt to find and click the 'next' button for pagination.
            # It's located within an <li> tag with class 'next', containing an <a> tag.
            # We wait for it to be clickable before attempting to click.
            next_button = WebDriverWait(driver, 5).until(
                EC.element_to_be_clickable((By.XPATH, "//li[@class='next']/a"))
            )
            next_button.click() # Click the 'next' button
            page_num += 1 # Increment the page counter
            print(f"Clicked 'next' button. Navigating to page {page_num}.")
            time.sleep(2) # Pause to allow the next page to fully load

        except (NoSuchElementException, TimeoutException):
            # If the 'next' button is not found or not clickable within the timeout,
            # it indicates that we have reached the last page of products.
            print("No 'next' button found or clickable. Assumed to be the last page.")
            break # Exit the while loop as there are no more pages.

    print(f"\n--- Finished Scraping. Total books found: {len(scraped_data)} ---")
    
    # --- Save Scraped Data to CSV File ---
    csv_file_name = "scraped_books_data.csv"
    if scraped_data:
        try:
            # Open the CSV file in write mode ('w'), 'newline=''' is important to prevent extra blank rows
            with open(csv_file_name, 'w', newline='', encoding='utf-8') as csvfile:
                # Update fieldnames to include all new extracted data points
                fieldnames = ['title', 'price', 'star_rating', 'availability', 'category']
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

                # Write the header row
                writer.writeheader()

                # Write all the scraped book data
                writer.writerows(scraped_data)
            print(f"\nSuccessfully saved {len(scraped_data)} books to '{csv_file_name}'.")
        except Exception as csv_error:
            print(f"\nError saving data to CSV: {csv_error}")
    else:
        print("\nNo data was scraped, so no CSV file was created.")

    # --- Validation Logic ---
    print("\n--- Starting Data Validations ---")
    validation_errors = [] # A list to store any validation errors found

    # Validation 1: Prices are not negative
    print("Validation: Checking if all prices are non-negative...")
    # Iterate through scraped_data, making sure to handle cases where 'price' key might be missing
    for i, item in enumerate(scraped_data):
        if 'price' in item and item["price"] < 0:
            error_msg = f"Validation Error: Price for '{item.get('title', 'N/A')}' (Index {i}) is negative: {item['price']:.2f}"
            print(f"  FAILED: {error_msg}")
            validation_errors.append(error_msg)
    # Re-check condition to ensure all prices are non-negative from the original source of truth
    if not any('price' in item and item["price"] < 0 for item in scraped_data):
        print("  PASSED: All prices are non-negative.")
    
    # Validation 2: Book titles are not empty
    print("Validation: Checking if all book titles are not empty...")
    # Iterate through scraped_data, making sure to handle cases where 'title' key might be missing or empty after strip()
    for i, item in enumerate(scraped_data):
        if 'title' not in item or not item["title"].strip():
            error_msg = f"Validation Error: Title for book at index {i} is empty or blank."
            print(f"  FAILED: {error_msg}")
            validation_errors.append(error_msg)
    # Re-check condition
    if not any('title' not in item or not item["title"].strip() for item in scraped_data):
        print("  PASSED: All book titles are not empty.")
    
    # New Validation 3: Star rating is one of the expected values
    print("Validation: Checking if star ratings are valid (One, Two, Three, Four, Five, N/A)...")
    valid_ratings = ["One", "Two", "Three", "Four", "Five", "N/A"]
    for i, item in enumerate(scraped_data):
        if 'star_rating' in item and item["star_rating"] not in valid_ratings:
            error_msg = f"Validation Error: Invalid star rating for '{item.get('title', 'N/A')}' (Index {i}): '{item['star_rating']}'"
            print(f"  FAILED: {error_msg}")
            validation_errors.append(error_msg)
    if not any('star_rating' in item and item["star_rating"] not in valid_ratings for item in scraped_data):
        print("  PASSED: All star ratings are valid.")

    # New Validation 4: Availability format (check if it's a number or 'N/A')
    print("Validation: Checking if availability is a number or 'N/A'...")
    for i, item in enumerate(scraped_data):
        if 'availability' in item and item["availability"] not in ["N/A", "Yes", "0"]: # Added "Yes" and "0" as valid states
            try:
                int(item["availability"]) # Try converting to int
            except ValueError:
                error_msg = f"Validation Error: Invalid availability format for '{item.get('title', 'N/A')}' (Index {i}): '{item['availability']}'"
                print(f"  FAILED: {error_msg}")
                validation_errors.append(error_msg)
    if not any('availability' in item and item["availability"] not in ["N/A", "Yes", "0"] and not str(item["availability"]).isdigit() for item in scraped_data):
        print("  PASSED: All availability entries are valid.")

    # New Validation 5: Category is not empty
    print("Validation: Checking if category is not empty...")
    for i, item in enumerate(scraped_data):
        if 'category' not in item or not item["category"].strip() or item["category"] == "N/A":
            error_msg = f"Validation Error: Category for '{item.get('title', 'N/A')}' (Index {i}) is empty or 'N/A'."
            print(f"  FAILED: {error_msg}")
            validation_errors.append(error_msg)
    if not any('category' not in item or not item["category"].strip() or item["category"] == "N/A" for item in scraped_data):
        print("  PASSED: All categories are not empty or 'N/A'.")


    # --- Final Test Result ---
    if not validation_errors:
        print("\n*** ALL VALIDATIONS PASSED! The data is valid. ***")
    else:
        print(f"\n!!! VALIDATIONS FAILED! Found {len(validation_errors)} error(s). Please review. !!!")
        for error in validation_errors:
            print(f" - {error}")

except Exception as e:
    # Catch any unexpected errors during the test execution
    print(f"An unexpected error occurred during the test: {e}")

finally:
    # This block ensures the browser is closed even if an error occurs
    if driver:
        driver.quit() # Close the browser window
        print("Browser (Firefox) closed.")
    print("Automated test finished.")