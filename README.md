# Audio Scraper

This project is a web scraper designed to extract entertainment news and other content from the [Ekantipur](https://ekantipur.com) website. It uses the Playwright library for browser automation and data extraction.

## Features

- Scrapes the top 5 entertainment news articles.
- Extracts metadata such as titles, URLs, and other attributes.
- Handles relative URLs and converts them to absolute URLs.
- Outputs the scraped data in JSON format.

## Project Structure

- `main.py`: Contains the main scraping logic for entertainment news.
- `scraper.py`: Includes utility functions for scraping and handling metadata.
- `output.json`: Stores the scraped data in JSON format.
- `pyproject.toml`: Project configuration file with dependencies and metadata.

## Requirements

- Python 3.13 or higher
- Playwright 1.59.0 or higher

## Installation

1. Clone the repository:
   ```bash
   git clone <repository-url>
   cd audio
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Install Playwright browsers:
   ```bash
   playwright install
   ```

## Usage

1. Run the scraper:
   ```bash
   python main.py
   ```

2. The scraped data will be saved in `output.json`.

## License

This project is licensed under the MIT License. See the LICENSE file for details.

## Acknowledgments

- [Ekantipur](https://ekantipur.com) for providing the content.
- [Playwright](https://playwright.dev) for the browser automation framework.