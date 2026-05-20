import os
import re
from typing import List
from playwright.sync_api import sync_playwright
from betnacional.models.odds import Match, Market, OddOutcome

def parse_championship_dom(page) -> List[Match]:
    matches = []
    
    # Locate all event list items
    event_items = page.locator("[data-testid='event-list-item']").all()
    print(f"Found {len(event_items)} event list items in DOM.")
    
    for item in event_items:
        try:
            # 1. Extract link and Event ID
            anchor = item.locator("a").first
            href = anchor.get_attribute("href") or ""
            # Expecting href like "/event/1/0/66886802"
            match_id_match = re.search(r"/event/\d+/\d+/(\d+)", href)
            if not match_id_match:
                continue
            event_id = match_id_match.group(1)
            
            # 2. Extract Home and Away Teams
            team_elements = item.locator("[data-testid='event-list-item-team']").all()
            if len(team_elements) < 2:
                continue
            home_team = team_elements[0].inner_text().strip()
            away_team = team_elements[1].inner_text().strip()
            
            # 3. Extract Date/Time
            time_el = item.locator("[data-testid='event-list-item-time-text']")
            time_text = ""
            if time_el.count() > 0:
                time_text = time_el.first.inner_text().strip()
            
            # 4. Extract Odds (market 1 - Resultado Final)
            # Find the odd elements for this event_id
            market_id = "1"
            outcomes = []
            
            # Home odd
            odd_1_el = item.locator(f"[data-testid='odd-{event_id}_{market_id}_1_']")
            if odd_1_el.count() > 0:
                val_text = odd_1_el.first.inner_text().strip()
                if val_text:
                    outcomes.append(OddOutcome(id="1", name=home_team, value=float(val_text)))
                    
            # Draw odd
            odd_2_el = item.locator(f"[data-testid='odd-{event_id}_{market_id}_2_']")
            if odd_2_el.count() > 0:
                val_text = odd_2_el.first.inner_text().strip()
                if val_text:
                    outcomes.append(OddOutcome(id="2", name="Empate", value=float(val_text)))
                    
            # Away odd
            odd_3_el = item.locator(f"[data-testid='odd-{event_id}_{market_id}_3_']")
            if odd_3_el.count() > 0:
                val_text = odd_3_el.first.inner_text().strip()
                if val_text:
                    outcomes.append(OddOutcome(id="3", name=away_team, value=float(val_text)))
            
            markets = []
            if outcomes:
                markets.append(Market(id=market_id, name="Resultado Final", outcomes=outcomes))
                
            matches.append(Match(
                id=event_id,
                homeTeam=home_team,
                awayTeam=away_team,
                startTime=time_text,
                sportName="Futebol",
                leagueName="Brasileirão Série A",
                markets=markets
            ))
        except Exception as e:
            print(f"Error parsing event item: {e}")
            
    return matches

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
        
        matches = parse_championship_dom(page)
        print(f"\nParsed {len(matches)} matches:")
        for idx, m in enumerate(matches):
            print(f"\nMatch {idx+1}: {m.home_team} vs {m.away_team} ({m.start_time}) - ID: {m.id}")
            for market in m.markets:
                print(f"  Market: {market.name}")
                for outcome in market.outcomes:
                    print(f"    - {outcome.name}: {outcome.value} (ID: {outcome.id})")
                    
        browser.close()

if __name__ == "__main__":
    main()
