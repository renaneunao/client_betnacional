import logging
import re
from typing import List
from playwright.sync_api import sync_playwright
from betnacional.models.odds import Match, Market, OddOutcome

logger = logging.getLogger("betnacional.scraper")

class ChampionshipScraper:
    """
    Scraper utilizing Playwright to load the Betnacional frontend,
    allow the WebSocket connection to fetch matches/odds, and parse them from the DOM.
    """
    
    def __init__(self, headless: bool = True):
        self.headless = headless

    def scrape_championship_matches(self, tournament_id: int, league_name: str = "") -> List[Match]:
        """
        Navigates to the tournament page, waits for elements to render, and parses matches/odds.
        
        Args:
            tournament_id: The platform ID of the tournament (e.g. 325 for Brasileirão Série A, 390 for Série B)
            league_name: Optional display name for the league. Auto-detected if empty.
            
        Returns:
            A list of Match models populated with their respective odds/outcomes.
        """
        url = f"https://betnacional.bet.br/events/1/0/{tournament_id}"
        logger.info("Starting browser to scrape tournament matches from %s...", url)
        
        matches = []
        
        with sync_playwright() as p:
            # Launch chromium in headless mode
            browser = p.chromium.launch(headless=self.headless)
            try:
                context = browser.new_context(
                    user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
                )
                page = context.new_page()
                
                # Navigate to the page with 'load' to ignore persistent analytics/tracking timeouts
                page.goto(url, wait_until="load", timeout=30000)
                
                # Wait 10 seconds for WebSocket odds updates to populate the DOM
                logger.info("Waiting for WebSocket data to populate the DOM...")
                page.wait_for_timeout(10000)
                
                # Query all event list item containers
                event_items = page.locator("[data-testid='event-list-item']").all()
                logger.info("Found %d event list items in the DOM.", len(event_items))
                
                for item in event_items:
                    try:
                        # 1. Extract the event detail link to parse the match/event ID
                        anchor = item.locator("a").first
                        href = anchor.get_attribute("href") or ""
                        # Expected format: "/event/1/0/{event_id}"
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
                        
                        # 3. Extract Start Date/Time
                        time_el = item.locator("[data-testid='event-list-item-time-text']")
                        time_text = ""
                        if time_el.count() > 0:
                            time_text = time_el.first.inner_text().strip()
                        
                        # 4. Extract Odds dynamically (data-testid format changed with RAMP provider)
                        market_id = "1"
                        outcomes = []
                        
                        odd_elements = item.locator(f"[data-testid^='odd-{event_id}_']").all()
                        
                        outcome_names = [home_team, "Empate", away_team]
                        outcome_ids = ["1", "2", "3"]
                        
                        for i, odd_el in enumerate(odd_elements[:3]):
                            try:
                                val_text = odd_el.inner_text().strip()
                                if val_text:
                                    outcomes.append(OddOutcome(
                                        id=outcome_ids[i],
                                        name=outcome_names[i],
                                        value=float(val_text)
                                    ))
                            except Exception:
                                pass
                        
                        markets = []
                        if outcomes:
                            markets.append(Market(id=market_id, name="Resultado Final", outcomes=outcomes))
                            
                        matches.append(Match(
                            id=event_id,
                            homeTeam=home_team,
                            awayTeam=away_team,
                            startTime=time_text,
                            sportName="Futebol",
                            leagueName=league_name or f"Torneio {tournament_id}",
                            markets=markets
                        ))
                    except Exception as e:
                        logger.warning("Error parsing individual event card: %s", e)
                        
            except Exception as e:
                logger.error("Error during championship scraping execution: %s", e)
            finally:
                browser.close()
                
        logger.info("Successfully scraped %d matches.", len(matches))
        return matches
