import os
import json
import time
import logging
from playwright.sync_api import sync_playwright, Response

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("capture-history")

OUTPUT_FILE = os.path.join("mitm_capture", "history_flows.json")
os.makedirs(os.path.dirname(OUTPUT_FILE), exist_ok=True)

captured_flows = []


def handle_response(response: Response):
    url = response.url
    request = response.request

    req_body = ""
    req_json = None
    if request.post_data:
        req_body = request.post_data
        try:
            req_json = json.loads(req_body)
        except Exception:
            pass

    resp_body = ""
    resp_json = None
    try:
        resp_body = response.text()
        try:
            resp_json = json.loads(resp_body)
        except Exception:
            pass
    except Exception as e:
        resp_body = f"[Error reading response text: {e}]"

    logger.info(f"Captured: {request.method} {url} -> {response.status}")

    flow_data = {
        "timestamp": time.time(),
        "method": request.method,
        "url": url,
        "request": {
            "headers": dict(request.headers),
            "body_raw": req_body,
            "body_json": req_json
        },
        "response": {
            "status_code": response.status,
            "headers": dict(response.headers),
            "body_raw": resp_body[:50000],
            "body_json": resp_json
        }
    }

    captured_flows.append(flow_data)

    try:
        with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
            json.dump(captured_flows, f, indent=2, ensure_ascii=False)
    except Exception as e:
        logger.error(f"Failed to write flows: {e}")


def main():
    logger.info("Starting Playwright browser (capturando TODO trafego, sem filtro de dominio)...")
    with sync_playwright() as p:
        browser = p.chromium.launch(
            headless=False,
            args=["--start-maximized"]
        )

        context = browser.new_context(
            no_viewport=True,
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        )

        page = context.new_page()
        page.on("response", handle_response)

        logger.info("Navigating to Betnacional...")
        page.goto("https://betnacional.bet.br", wait_until="load")

        print()
        print("=" * 80)
        print("  NAVEGADOR ATIVO - CAPTURANDO TODO O TRAFEGO (SEM FILTROS)")
        print()
        print("  1. Se necessario, faca login manualmente")
        print("  2. Navegue ate a pagina de historico de apostas (Minha Conta > Bilhetes/Histórico)")
        print("  3. Interaja com a pagina (filtros, paginas, etc.)")
        print("  4. FECHE O NAVEGADOR quando terminar para finalizar a captura")
        print("=" * 80)
        print()

        while True:
            try:
                if not browser.is_connected():
                    break
                page.wait_for_timeout(1000)
            except Exception:
                break

        logger.info("Navegador fechado. Aguardando 5s para finalizar captura de respostas pendentes...")
        time.sleep(5)

        try:
            cookies = context.cookies()
            cookies_file = os.path.join("mitm_capture", "history_cookies.json")
            with open(cookies_file, "w") as f:
                json.dump(cookies, f, indent=2)
            logger.info(f"Cookies salvos em {cookies_file}")
        except Exception as e:
            logger.error(f"Falha ao salvar cookies: {e}")

        logger.info(f"Captura finalizada. Total de flows capturados: {len(captured_flows)}")
        logger.info(f"Resultado salvo em: {OUTPUT_FILE}")
        print(f"\n>>> {len(captured_flows)} flows capturados em {OUTPUT_FILE}")


if __name__ == "__main__":
    main()
