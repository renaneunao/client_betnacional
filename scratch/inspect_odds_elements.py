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
        
        # We know one of the odds is "1.93". Let's search for elements containing "1.93"
        print("\nSearching for elements with text '1.93':")
        elements = page.locator("*:has-text('1.93')").all()
        for idx, el in enumerate(elements):
            tag_name = el.evaluate("e => e.tagName")
            class_name = el.get_attribute("class") or ""
            inner_text = el.inner_text()
            print(f"[{idx}] Tag: {tag_name}, Class: {class_name[:100]}, Text: {repr(inner_text[:100])}")
            
            # Let's inspect its attributes
            attrs = el.evaluate("e => Array.from(e.attributes).map(a => [a.name, a.value])")
            print(f"    Attrs: {attrs}")
            
        # Let's also search for elements having data-testid or class names related to odds
        # Let's check all elements that have class names containing 'odd' or data-testid containing 'odd'
        print("\nSearching for odds containers or buttons:")
        odds_els = page.locator("[class*='odd'], [class*='Odd'], [data-testid*='odd'], [data-testid*='Outcome']").all()
        print(f"Found {len(odds_els)} elements matching odds class/testid.")
        for idx, el in enumerate(odds_els[:15]):
            tag_name = el.evaluate("e => e.tagName")
            class_name = el.get_attribute("class") or ""
            data_testid = el.get_attribute("data-testid") or ""
            inner_text = el.inner_text()
            print(f"[{idx}] Tag: {tag_name}, testid: {data_testid}, Class: {class_name[:60]}, Text: {repr(inner_text)}")
            
        browser.close()

if __name__ == "__main__":
    main()
