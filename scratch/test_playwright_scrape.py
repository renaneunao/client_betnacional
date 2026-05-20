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
        # Use wait_until="load" to avoid timeout due to tracking/websockets
        page.goto(url, wait_until="load", timeout=30000)
        
        print("Waiting 10 seconds for content to load...")
        page.wait_for_timeout(10000)
        
        # Take a screenshot to verify what it sees
        screenshot_path = os.path.join("scratch", "championship_page.png")
        page.screenshot(path=screenshot_path)
        print(f"Saved screenshot to {screenshot_path}")
        
        # Print page title
        print(f"Page Title: {page.title()}")
        
        # Let's search for typical sportsbook text like "Vasco", "Flamengo", etc. in the page text
        content = page.content()
        print(f"Page content length: {len(content)}")
        
        # Let's find some buttons or text content on the page
        elements = page.locator("div, span, button").all_inner_texts()
        print(f"Total element texts: {len(elements)}")
        
        teams_found = []
        for text in elements:
            if not text:
                continue
            # Look for typical Brazilian team names
            for team in ["Flamengo", "Palmeiras", "São Paulo", "Corinthians", "Fluminense", "Vasco", "Botafogo", "Cruzeiro"]:
                if team.lower() in text.lower() and text not in teams_found:
                    teams_found.append(text)
                    
        print("Found team texts in DOM:")
        for idx, t in enumerate(teams_found[:30]):
            print(f" {idx}: {repr(t)}")
            
        # Find elements that contain odds or event IDs
        # Let's write all divs with their classes or text that seem like matches
        # Typically, a match row has team names and odds
        # Let's search for divs containing team names and dump their HTML to see structure
        for team in ["Flamengo", "Palmeiras", "São Paulo", "Mirassol"]:
            idx = content.lower().find(team.lower())
            if idx != -1:
                print(f"\nHTML snippet around '{team}':")
                print(content[max(0, idx-500):min(len(content), idx+1500)])
                print("=" * 80)
                break
                
        browser.close()

if __name__ == "__main__":
    main()
