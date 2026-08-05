# Working Notes

## 1. Selectors I Found

Before writing the scraper, I inspected the Kantipur website using Chrome DevTools. I needed to scrape two different sections: Entertainment news and Cartoon of the Day.

I found that these two pages use different HTML structures, so I could not reuse exactly the same selectors for both.

### Entertainment Page

For the Entertainment page, each article is contained inside:

`div.category`

Inside each article, I found:

- Article container: `div.category`
- Inner wrapper: `div.category-inner-wrapper`
- Content/details: `div.category-description`
- Title/link: `div.category-description h2 a`
- Author: `div.author-name`
- Time: `div.time-wrapper`
- Image container: `div.category-image`
- Image: `div.category-image img`

The article URL is available from the `href` attribute of the title's `<a>` element.

### Cartoon of the Day Page

The Cartoon page has a different structure.

The main section is:

`section.cartoon-main-wrapper`

Each cartoon is displayed inside a grid column and contains a `div.cartoon-wrapper`.

The selectors I identified were:

- Main section: `section.cartoon-main-wrapper`
- Cartoon container: `div.cartoon-wrapper`
- Image container: `div.cartoon-image`
- Image: `div.cartoon-image figure a img`
- Description: `div.cartoon-description`

I also noticed that the cartoon image is wrapped inside a `<figure>` and `<a>` element.

The `<img>` element contains the image URL in its `src` attribute.

### Things I Noticed

The most important thing I noticed was that the Entertainment and Cartoon pages do not use the same HTML structure.

For example, Entertainment articles use:

`div.category`

while cartoons use:

`div.cartoon-wrapper`

The image selectors are also different:

Entertainment:

`div.category-image img`

Cartoon:

`div.cartoon-image figure a img`

Because of this, I inspected each page separately in DevTools instead of assuming that one set of selectors would work for the entire website.

I also checked multiple cards on each page to make sure the structure was repeated before using the selectors in my Playwright scraper.

---

## 2. What I Asked the AI

I used cursor while developing the scraper.

The main prompts I used were:

> Write a Python Playwright script to scrape the Entertainment section from a news website. Wait for the page to load completely, locate the Entertainment section, and extract the headline, article URL, image URL, and summary.

> How can I use Playwright selectors to scrape the "Cartoon of the Day" section? Show me how to locate the correct elements using CSS selectors and extract the title, image URL, and article link.

> I have extracted the data using Playwright. How can I organize the results into a JSON file with separate keys for the Entertainment section and Cartoon of the Day, while handling missing elements safely?

I used AI mainly to help with the Playwright implementation and handling the extracted data. I verified the selectors myself using Chrome DevTools rather than relying only on selectors suggested by AI.

---

## 3. One Thing It Got Wrong

One issue with the initial AI-generated approach was that it assumed similar or generic selectors could be used for the content.

After checking the website manually in Chrome DevTools, I found that the Entertainment page and Cartoon page have different DOM structures.

For example, Entertainment articles are contained in:

`div.category`

but cartoons are contained in:

`div.cartoon-wrapper`

Similarly, the Entertainment image is under:

`div.category-image img`

while the Cartoon image is under:

`div.cartoon-image figure a img`

I caught this by inspecting both pages in DevTools and testing the selectors against the actual elements.

I changed the scraper to use separate selectors for each page structure instead of trying to use one generic selector for both.