import json
import os

FLOWS_FILE = os.path.join("mitm_capture", "captured_flows.json")

def main():
    if not os.path.exists(FLOWS_FILE):
        return

    with open(FLOWS_FILE, "r", encoding="utf-8") as f:
        flows = json.load(f)

    print("Checking for WebSocket connections or messages...")
    ws_count = 0
    for idx, flow in enumerate(flows):
        url = flow.get("url", "")
        # WebSocket connections usually start with ws:// or wss:// or contain websocket/socket.io
        if "ws" in url or "socket" in url or "pusher" in url or "signalr" in url or "centrifuge" in url:
            if "doubleclick" in url or "google" in url:
                continue
            ws_count += 1
            print(f"[{idx}] {flow.get('method', 'GET')} {url}")
            
    print(f"Total WebSocket/Socket flows found: {ws_count}")

if __name__ == "__main__":
    main()
