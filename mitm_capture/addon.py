import json
import os
import logging
from mitmproxy import http

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("betnacional-interceptor")

class BetnacionalInterceptor:
    def __init__(self):
        self.output_file = os.path.join("mitm_capture", "captured_flows.json")
        self.flows = []
        logger.info("Betnacional Interceptor initialized. Output file will be: %s", self.output_file)
        
        # Ensure the directory exists
        os.makedirs(os.path.dirname(self.output_file), exist_ok=True)
        
        # Load existing flows if they exist to append
        if os.path.exists(self.output_file):
            try:
                with open(self.output_file, "r", encoding="utf-8") as f:
                    self.flows = json.load(f)
                logger.info("Loaded %d existing flows from %s", len(self.flows), self.output_file)
            except Exception as e:
                logger.warning("Could not load existing flows: %s", e)

    def request(self, flow: http.HTTPFlow):
        host = flow.request.pretty_host
        if "betnacional.com" in host:
            # Skip noise like static assets, fonts, etc.
            path = flow.request.path
            if any(path.endswith(ext) for ext in [".js", ".css", ".png", ".jpg", ".jpeg", ".gif", ".svg", ".ico", ".woff", ".woff2", ".ttf"]):
                return
            
            logger.info(">>> INTERCEPTED REQUEST: %s %s", flow.request.method, flow.request.pretty_url)

    def response(self, flow: http.HTTPFlow):
        host = flow.request.pretty_host
        if "betnacional.com" in host:
            path = flow.request.path
            # Skip noise
            if any(path.endswith(ext) for ext in [".js", ".css", ".png", ".jpg", ".jpeg", ".gif", ".svg", ".ico", ".woff", ".woff2", ".ttf"]):
                return

            logger.info("<<< INTERCEPTED RESPONSE: %d for %s", flow.response.status_code, flow.request.pretty_url)
            
            # Parse request body (if JSON)
            req_content = flow.request.text or ""
            try:
                req_json = json.loads(req_content)
            except Exception:
                req_json = None

            # Parse response body (if JSON)
            resp_content = flow.response.text or ""
            try:
                resp_json = json.loads(resp_content)
            except Exception:
                resp_json = None

            flow_data = {
                "timestamp": flow.request.timestamp_start,
                "method": flow.request.method,
                "url": flow.request.pretty_url,
                "path": flow.request.path,
                "request": {
                    "headers": dict(flow.request.headers),
                    "cookies": dict(flow.request.cookies),
                    "body_raw": req_content,
                    "body_json": req_json
                },
                "response": {
                    "status_code": flow.response.status_code,
                    "headers": dict(flow.response.headers),
                    "cookies": dict(flow.response.cookies),
                    "body_raw": resp_content[:50000],  # cap length to avoid bloated files
                    "body_json": resp_json
                }
            }

            self.flows.append(flow_data)
            self.save_flows()

    def save_flows(self):
        try:
            with open(self.output_file, "w", encoding="utf-8") as f:
                json.dump(self.flows, f, indent=2, ensure_ascii=False)
            logger.info("Saved %d flows to %s", len(self.flows), self.output_file)
        except Exception as e:
            logger.error("Failed to save flows: %s", e)

addons = [BetnacionalInterceptor()]
