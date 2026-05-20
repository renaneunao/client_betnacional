import json
import os

FLOWS_FILE = os.path.join("mitm_capture", "captured_flows.json")

def main():
    if not os.path.exists(FLOWS_FILE):
        return

    with open(FLOWS_FILE, "r", encoding="utf-8") as f:
        flows = json.load(f)

    flow = flows[226]
    resp_json = flow.get("response", {}).get("body_json", {})
    
    json_str = json.dumps(resp_json)
    print(f"Flow 226 response json size (chars): {len(json_str)}")
    
    teams = ["Coritiba", "Bahia", "Vasco", "Bragantino", "Remo", "Athletico", "Corinthians", "Cruzeiro", "São Paulo", "Botafogo", "Vitória", "Internacional", "Grêmio", "Santos", "Flamengo", "Palmeiras", "Mirassol", "Fluminense"]
    
    found = []
    for team in teams:
        if team.lower() in json_str.lower():
            found.append(team)
            
    print(f"Teams found in flow 226: {found}")

if __name__ == "__main__":
    main()
