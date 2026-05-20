import os
import json
from playwright.sync_api import sync_playwright

def main():
    print("Launching Playwright...")
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        )
        page = context.new_page()
        
        url = "https://betnacional.bet.br/events/1/0/325"
        print(f"Navigating to {url}...")
        page.goto(url, wait_until="load", timeout=30000)
        page.wait_for_timeout(10000)
        
        # Let's query event list items
        # Usually it's in a container. Let's find all anchors under elements having 'event' or similar class
        # In our snippet: ...</a><div data-testid="event-list-item-footer"...
        # Let's inspect elements with data-testid="event-list-item-team" or its parents
        print("Finding match anchors or containers...")
        
        # Let's print all links containing '/detail/' or '/event/' or numbers
        links = page.locator("a").all()
        print(f"Total links: {len(links)}")
        for idx, link in enumerate(links):
            href = link.get_attribute("href") or ""
            if any(p in href for p in ["/event/", "/detail/", "/match/", "/sport/"]):
                print(f"Link {idx}: href={href}, text={repr(link.inner_text()[:100])}")
        
        # Let's find buttons (these are typically the odds buttons!)
        buttons = page.locator("button").all()
        print(f"\nTotal buttons: {len(buttons)}")
        count = 0
        for idx, btn in enumerate(buttons):
            text = btn.inner_text()
            # If it's a number (odd), print it and its attributes
            if text and any(char.isdigit() for char in text):
                attrs = page.evaluate("el => { return Array.from(el.attributes).map(a => [a.name, a.value]); }", btn.element_handle())
                print(f"Button {idx}: text={repr(text)}, attrs={attrs}")
                count += 1
                if count >= 15:
                    break
                    
        browser.close()

if __name__ == "__main__":
    main()
