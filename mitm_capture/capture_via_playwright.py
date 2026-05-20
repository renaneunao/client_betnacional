import os
import sys
import json
import time
import logging
from playwright.sync_api import sync_playwright, Response, Request

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("playwright-capture")

# Output path
OUTPUT_FILE = os.path.join("mitm_capture", "captured_flows.json")
os.makedirs(os.path.dirname(OUTPUT_FILE), exist_ok=True)

# List to hold captured HTTP exchanges
captured_flows = []

def should_capture(url: str) -> bool:
    """Filter out static assets and noise, focusing on betnacional API calls."""
    if "betnacional" not in url:
        return False
    # Exclude common static extensions
    path = url.split("?")[0].lower()
    for ext in [".js", ".css", ".png", ".jpg", ".jpeg", ".gif", ".svg", ".ico", ".woff", ".woff2", ".ttf"]:
        if path.endswith(ext):
            return False
    return True

def handle_response(response: Response):
    url = response.url
    if not should_capture(url):
        return

    request = response.request
    logger.info(f"Captured: {request.method} {url} -> Status {response.status}")

    # Extract request payload
    req_body = ""
    req_json = None
    if request.post_data:
        req_body = request.post_data
        try:
            req_json = json.loads(req_body)
        except Exception:
            pass

    # Extract response body
    resp_body = ""
    resp_json = None
    try:
        # Some responses might be empty or binary
        resp_body = response.text()
        try:
            resp_json = json.loads(resp_body)
        except Exception:
            pass
    except Exception as e:
        resp_body = f"[Error reading response text: {e}]"

    # Capture cookies from browser context for this request/response if possible
    # We can get them later, but let's record what was sent in the headers
    flow_data = {
        "timestamp": time.time(),
        "method": request.method,
        "url": url,
        "request": {
            "headers": request.headers,
            "body_raw": req_body,
            "body_json": req_json
        },
        "response": {
            "status_code": response.status,
            "headers": response.headers,
            "body_raw": resp_body[:50000],  # cap long responses
            "body_json": resp_json
        }
    }
    
    captured_flows.append(flow_data)
    
    # Save incrementally
    try:
        with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
            json.dump(captured_flows, f, indent=2, ensure_ascii=False)
    except Exception as e:
        logger.error(f"Failed to write captured flows: {e}")

def main():
    # Load credentials from .env
    from dotenv import load_dotenv
    load_dotenv()
    
    cpf = os.getenv("BETNACIONAL_CPF", "09446024609")
    password = os.getenv("BETNACIONAL_PASSWORD", "!Senhas123")

    logger.info("Starting Playwright...")
    with sync_playwright() as p:
        # Launch Chrome / Chromium in headful mode so we can see and interact
        # Using a default viewport and no stealth plugins for initial capture,
        # but mimicking normal browser settings.
        browser = p.chromium.launch(
            headless=False,
            args=["--start-maximized"]
        )
        
        # Create context with maximized viewport
        context = browser.new_context(
            no_viewport=True,
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        )
        
        page = context.new_page()
        
        # Subscribe to response events
        page.on("response", handle_response)
        
        logger.info("Navigating to Betnacional...")
        page.goto("https://betnacional.bet.br", wait_until="load")
        
        # Try to automate clicking the login button and filling credentials
        try:
            logger.info("Attempting auto-login...")
            
            # Look for Login / Entrar button
            # Usually it says "Entrar" or has a class containing login
            login_btn = None
            for selector in ["text=Entrar", "button:has-text('Entrar')", ".login-button", "a:has-text('Entrar')"]:
                try:
                    if page.locator(selector).is_visible(timeout=2000):
                        login_btn = page.locator(selector)
                        break
                except Exception:
                    continue
            
            if login_btn:
                logger.info("Clicking login button...")
                login_btn.click()
                page.wait_for_timeout(1000)
                
                # Fill fields. We'll search for typical input selectors
                # E.g. input with placeholder CPF or user/login, and password
                cpf_input = None
                pass_input = None
                
                # Find CPF/user input
                for selector in ["input[placeholder*='CPF']", "input[placeholder*='User']", "input[type='text']", "input[name='login']", "input[name='username']"]:
                    try:
                        if page.locator(selector).is_visible(timeout=2000):
                            cpf_input = page.locator(selector)
                            break
                    except Exception:
                        continue
                        
                # Find password input
                for selector in ["input[type='password']", "input[name='password']"]:
                    try:
                        if page.locator(selector).is_visible(timeout=2000):
                            pass_input = page.locator(selector)
                            break
                    except Exception:
                        continue
                
                if cpf_input and pass_input:
                    logger.info("Filling credentials...")
                    cpf_input.fill(cpf)
                    page.wait_for_timeout(500)
                    pass_input.fill(password)
                    page.wait_for_timeout(500)
                    
                    # Submit login. Look for submit button or press Enter
                    submit_btn = None
                    for selector in ["button[type='submit']", "button:has-text('Entrar')", ".submit-btn", "form button"]:
                        try:
                            if page.locator(selector).is_visible(timeout=1000):
                                submit_btn = page.locator(selector)
                                break
                        except Exception:
                            continue
                    
                    if submit_btn:
                        logger.info("Clicking submit button...")
                        submit_btn.click()
                    else:
                        logger.info("Pressing Enter on password field...")
                        pass_input.press("Enter")
                else:
                    logger.warning("Could not find credentials inputs automatically. Please log in manually.")
            else:
                logger.warning("Could not find 'Entrar' button automatically. Please log in manually.")
                
        except Exception as e:
            logger.warning(f"Auto-login automation helper failed: {e}. Please log in manually in the opened browser window.")

        print("\n" + "="*80)
        print(" BROWSER ACTIVE - PLEASE LOG IN MANUALLY IF NEEDED AND BROWSE THE SITE")
        print(" Close the browser window when you are finished to complete capture.")
        print("="*80 + "\n")
        
        # Keep browser open until user closes it or script is interrupted
        while True:
            try:
                # Check if browser is still connected
                if not browser.is_connected():
                    break
                page.wait_for_timeout(1000)
            except Exception:
                break
                
        # Save cookies at the end of session for inspection
        try:
            cookies = context.cookies()
            cookies_file = os.path.join("mitm_capture", "cookies.json")
            with open(cookies_file, "w") as f:
                json.dump(cookies, f, indent=2)
            logger.info(f"Saved session cookies to {cookies_file}")
        except Exception as e:
            logger.error(f"Failed to save cookies: {e}")

        logger.info(f"Capture finished. Total API flows captured: {len(captured_flows)}")
        logger.info(f"Results saved in: {OUTPUT_FILE}")

if __name__ == "__main__":
    main()
