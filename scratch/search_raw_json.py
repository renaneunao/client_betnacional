import os

JSON_FILE = os.path.join("scratch", "325_details.json")

def main():
    if not os.path.exists(JSON_FILE):
        print("File not found")
        return

    with open(JSON_FILE, "r", encoding="utf-8") as f:
        content = f.read()

    terms = ["Chapecoense", "Remo", "Athletico", "Bragantino", "Mirassol", "Fluminense", "Vasco", "Flamengo", "Palmeiras", "Corinthians", "São Paulo"]
    for term in terms:
        idx = content.lower().find(term.lower())
        if idx != -1:
            print(f"Found '{term}' at index {idx}!")
            print(f"Snippet: {content[max(0, idx-50):min(len(content), idx+100)]}")
            print("-" * 50)
        else:
            print(f"'{term}' not found.")

if __name__ == "__main__":
    main()
