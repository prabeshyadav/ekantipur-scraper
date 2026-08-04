# Ekantipur Scraper

A web scraper that extracts entertainment news and the cartoon of the day from [Ekantipur](https://ekantipur.com). It uses [Playwright](https://playwright.dev) for browser automation and data extraction.

## Features

- Scrapes the top 5 entertainment news articles.
- Scrapes the cartoon of the day.
- Extracts metadata such as titles, image URLs, category, and author.
- Resolves relative URLs to absolute URLs.
- Writes scraped data to JSON (UTF-8, Nepali text preserved).

## Project Structure

- `scraper.py` — Main scraper script (entry point).
- `main.py` — Placeholder (not used).
- `output.json` — Generated scrape output (created when you run the scraper).
- `pyproject.toml` — Project metadata and dependencies (used by `uv`).
- `requirements.txt` — Pip-compatible dependency list.
- `.env.example` — Example environment variables (copy to `.env` for local config).

## Requirements

- Python 3.13 or higher
- Playwright 1.59.0 or higher

## Installation

### Option A: Using uv (recommended)

1. Clone the repository:
   ```bash
   git clone <repository-url>
   cd ekantipur-scraper
   ```

2. Install dependencies:
   ```bash
   uv sync
   ```

3. Install Playwright browsers:
   ```bash
   uv run playwright install chromium
   ```

### Option B: Using pip

1. Clone the repository and create a virtual environment:
   ```bash
   git clone <repository-url>
   cd ekantipur-scraper
   python -m venv .venv
   source .venv/bin/activate
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Install Playwright browsers:
   ```bash
   playwright install chromium
   ```

### Environment variables (optional)

Copy the example env file and adjust values if needed:

```bash
cp .env.example .env
```

Available variables (placeholders for local config; not yet read by `scraper.py`):

| Variable     | Default                    | Description                          |
|--------------|----------------------------|--------------------------------------|
| `BASE_URL`   | `https://ekantipur.com`    | Site base URL                        |
| `OUTPUT_JSON`| `output.json`              | Output file path                     |
| `HEADLESS`   | `false`                    | Run browser without a visible window |

## Usage

Run the scraper:

```bash
# with uv
uv run python scraper.py

# with pip / activated venv
python scraper.py
```

The scraped data is saved to `output.json` in the project root. This file is generated output and should not be committed to git.

Example output shape:

```json
{
  "entertainment news": [
    {
      "title": "...",
      "image_url": "...",
      "category": "...",
      "author": "..."
    }
  ],
  "cartoon of the day": {
    "title": "...",
    "image_url": "...",
    "author": "..."
  }
}
```

## Acknowledgments

- [Ekantipur](https://ekantipur.com) for providing the content.
- [Playwright](https://playwright.dev) for the browser automation framework.
