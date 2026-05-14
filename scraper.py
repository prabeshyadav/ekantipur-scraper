import json
from pathlib import Path
from urllib.parse import urljoin

from playwright.sync_api import sync_playwright


# Site origin only — resolved URLs for listings come from this (not editorial content).
BASE_URL = "https://ekantipur.com"
ENTERTAINMENT_URL = urljoin(BASE_URL, "/entertainment")
CARTOON_URL = urljoin(BASE_URL, "/cartoon")

# Written relative to the process working directory when the script is run.
OUTPUT_JSON = Path("output.json")


def scrape_section_label(page):
    """
    Read the category/section title the CMS exposes for the current page.

    Kantipur sets `meta[property="og:title"]` to the section name (e.g. entertainment).
    This keeps the `category` field aligned with whatever the live HTML advertises.
    """
    meta = page.query_selector('meta[property="og:title"]')
    if not meta:
        return None
    content = meta.get_attribute("content")
    return content.strip() if content else None


def safe_text(element):
    """
    Read visible text via Playwright's inner_text() after stripping whitespace.

    Used where we care about rendered text (e.g. cartoon captions). Returns None when
    the node is absent so callers can treat missing copy as a null author/title without
    raising.
    """
    return element.inner_text().strip() if element else None


def safe_attr(element, attr):
    """
    Read a DOM attribute without assuming the element exists.

    Returns None if the element is missing or the attribute is unset—callers normalize
    that to JSON null instead of inventing placeholder strings for authors or URLs.
    """
    return element.get_attribute(attr) if element else None


def make_full_url(url):
    """
    Resolve listing-page relative paths (e.g. /news/...) against BASE_URL.

    Kantipur often emits root-relative hrefs and image paths; urljoin keeps extraction
    stable without hard-coding each pattern. Empty or falsy input yields None so JSON
    can use null for missing media links.
    """
    if not url:
        return None

    return urljoin(BASE_URL, url)


def get_entertainment_news(page):
    """
    Collect exactly five entertainment rows from the live entertainment listing.

    Selectors mirror Kantipur's category listing markup: each story is a
    `.category-inner-wrapper` row; the headline lives in `h2 a`, the teaser image in
    `.category-image img`, and the byline in `.author-name a`. Those hooks match the
    layout classes the site uses for category grids so we avoid brittle full-page XPath.

    Scroll / lazy loading: above-the-fold images often keep placeholders in `src` until
    the row intersects the viewport. A small `window.scrollBy` plus a short wait nudges
    lazy-loaded `<img>` nodes to populate `src`, `data-src`, or `data-srcset` before we
    read attributes—otherwise thumbnails stay blank or point at spacer GIFs.

    Author null handling: if `.author-name a` is missing or its text is empty after strip,
    we leave `author` as Python None so JSON exports `"author": null`. Padding slots
    (when fewer than five rows scrape successfully) use the same schema with `author`:
    None rather than empty strings, so consumers can distinguish “unknown” from “blank”.

    Category: taken from `scrape_section_label` (Open Graph title from the loaded page),
    not from string literals in code.
    """
    news_list = []
    section_category = None

    try:
        page.goto(ENTERTAINMENT_URL)
        # Wait until the feed skeleton has rendered at least one `.category-inner-wrapper`.
        page.wait_for_selector(".category-inner-wrapper")
        section_category = scrape_section_label(page)
        # Scroll triggers lazy images below the fold; timeout gives network/decoding time.
        page.evaluate("window.scrollBy(0, 800)")
        page.wait_for_timeout(2000)
        # .category-inner-wrapper: collect cards; we may need more than five rows if some fail.
        cards = page.query_selector_all(".category-inner-wrapper")
    except Exception as exc:
        print(f"get_entertainment_news: page load or listing wait failed: {exc}")
        cards = []

    placeholder = {
        "title": None,
        "image_url": None,
        "category": section_category,
        "author": None,
    }

    for card in cards:
        if len(news_list) >= 5:
            break
        try:
            # h2 a: primary headline link inside the card (story title).
            title_el = card.query_selector("h2 a")
            title = None
            if title_el:
                raw_title = title_el.text_content()
                title = raw_title.strip() if raw_title else None

            # .category-image img: lead thumbnail in the image column of the card.
            img_el = card.query_selector(".category-image img")
            img_url = None
            if img_el:
                img_url = (
                    img_el.get_attribute("src")
                    or img_el.get_attribute("data-src")
                    or img_el.get_attribute("data-srcset")
                )

            # .author-name a: byline link next to the author label.
            author_el = card.query_selector(".author-name a")
            author = None
            if author_el:
                raw_author = author_el.text_content()
                author = raw_author.strip() if raw_author else None

            news_list.append({
                "title": title,
                "image_url": make_full_url(img_url) if img_url else None,
                "category": section_category,
                "author": author,
            })
        except Exception as exc:
            print(f"get_entertainment_news: skipped one card due to extraction error: {exc}")
            continue

    while len(news_list) < 5:
        news_list.append(dict(placeholder))

    return news_list[:5]


def get_cartoon_of_the_day(page):
    """
    Return one cartoon object parsed from the live cartoon listing.

    Selectors: `.cartoon-wrapper` scopes one cartoon tile; `.cartoon-description p` holds
    the caption line the CMS outputs (typically "title - author"). The art link is read
    from `.cartoon-image figure a` (`href`), with a bare `img` fallback when the figure
    link is absent.

    Titles, image URLs, and author names come only from those DOM nodes and caption text.
    When nothing usable is found, fields are JSON null—no placeholder editorial strings.
    """
    try:
        page.goto(CARTOON_URL)
        page.wait_for_selector(".cartoon-wrapper", timeout=15000)
    except Exception as exc:
        print(f"get_cartoon_of_the_day: page load or cartoon listing wait failed: {exc}")
        return {"title": None, "image_url": None, "author": None}

    try:
        cartoons = page.query_selector_all(".cartoon-wrapper")

        for cartoon in cartoons:
            try:
                # .cartoon-description p: caption line, often "title - author".
                desc_el = cartoon.query_selector(".cartoon-description p")
                full_desc = safe_text(desc_el)

                if not full_desc or "-" not in full_desc:
                    continue

                parts = full_desc.split("-")
                author = parts[1].strip()

                if not author:
                    continue

                # .cartoon-image figure a: link wrapping the cartoon art (full-size href).
                image_el = cartoon.query_selector(".cartoon-image figure a")
                # Bare img: fallback if the figure link is missing but an image tag exists.
                img_fallback = cartoon.query_selector("img")
                image_url = safe_attr(image_el, "href") or safe_attr(img_fallback, "src")

                return {
                    "title": parts[0].strip(),
                    "image_url": make_full_url(image_url),
                    "author": author,
                }
            except Exception as exc:
                print(f"get_cartoon_of_the_day: skipped one cartoon block: {exc}")
                continue

        return {"title": None, "image_url": None, "author": None}

    except Exception as exc:
        print(f"get_cartoon_of_the_day: fatal error: {exc}")
        return {"title": None, "image_url": None, "author": None}


def save_json(data):
    """
    Persist the scraped structure to OUTPUT_JSON (current working directory).

    `ensure_ascii=False` keeps Nepali script and punctuation literal in the file (no
    `\\uXXXX` escapes), which matters for downstream tools that display or diff Nepali
    headlines and categories. Indentation is fixed for human review in version control.
    """
    with OUTPUT_JSON.open("w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)


def main():
    """
    Drive Chromium once: open Kantipur with neutral locale headers, run the two scrapers,
    and write the combined payload.

    Entertainment uses in-page selectors and scroll-assisted lazy images; cartoon uses
    caption-based parsing from live DOM. The exported root keys are fixed contract
    strings for the five-item list and single cartoon object.
    """
    with sync_playwright() as p:

        browser = p.chromium.launch(
            headless=False
        )

        context = browser.new_context(
            locale="en-US"
        )

        page = context.new_page()

        page.set_extra_http_headers({
            "Accept-Language": "en-US,en;q=0.9"
        })

        entertainment_news = get_entertainment_news(page)
        cartoon_of_the_day = get_cartoon_of_the_day(page)

        final_data = {
            "entertainment news": entertainment_news,
            "cartoon of the day": cartoon_of_the_day,
        }

        save_json(final_data)

        print(f"\n{OUTPUT_JSON.resolve()} created successfully")

        browser.close()


if __name__ == "__main__":
    main()
