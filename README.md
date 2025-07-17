# BooksToScrape_Selenium_Project

## 🎥 **VIDEO DEMONSTRATION**
https://github.com/user-attachments/assets/fe66a321-74d0-4c32-b2ae-78829da73ecb

## Automated Web Scraping and Data Validation using Selenium and Python

This project demonstrates a robust web scraping solution built with **Selenium** and **Python**. It automates the extraction of book data from the "Books to Scrape" website (http://books.toscrape.com/), saves the collected information into a structured CSV file, and performs automated data quality validations.

This project is ideal for showcasing skills in:
* **Web Automation & Scraping:** Using Selenium WebDriver to interact with dynamic web pages.
* **Data Extraction:** Identifying and extracting specific data points (title, price, rating, availability, category).
* **Pagination Handling:** Navigating through multiple pages of content.
* **Data Persistence:** Saving scraped data to a structured format (CSV).
* **Data Validation:** Implementing automated checks to ensure data quality and integrity.
* **Error Handling:** Gracefully managing potential issues during scraping.
* **Python Programming:** Writing clean, modular, and well-commented Python code.

## 🚀 Features

* **Automated Browser Control:** Launches and controls a Firefox browser to simulate user interaction.
* **Dynamic Data Scraping:** Extracts book title, price, star rating, stock availability, and category.
* **Pagination Support:** Automatically navigates through the first 5 pages of the website to collect a comprehensive dataset (configurable).
* **CSV Export:** Saves all scraped data into a `scraped_books_data.csv` file for easy analysis.
* **Automated Data Validations:**
    * Verifies that all book prices are non-negative.
    * Ensures that all book titles are not empty.
    * Checks if star ratings are in an expected format (e.g., "One", "Two", "N/A").
    * Validates that availability is a numeric value or "N/A" / "Yes" / "0".
    * Confirms that categories are not empty or "N/A".
* **Clear Console Output:** Provides real-time feedback on scraping progress and validation results.
* **Graceful Error Handling:** Includes `try-except` blocks to manage common Selenium exceptions and ensure the browser closes properly.

## 🛠️ Technologies Used

* **Python 3.x**
* **Selenium WebDriver:** For browser automation.
* **`webdriver_manager`:** For automatic management and download of WebDriver binaries (GeckoDriver for Firefox).
* **`csv` module:** Python's built-in module for CSV file operations.
* **Firefox Browser**
