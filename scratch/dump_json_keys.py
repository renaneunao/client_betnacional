import json
import os

JSON_FILE = os.path.join("scratch", "325_details.json")
OUTPUT_FILE = os.path.join("scratch", "json_structure.txt")

def dump_keys_recursively(data, level=0, out_lines=None):
    if out_lines is None:
        out_lines = []
    
    indent = "  " * level
    if isinstance(data, dict):
        for k, v in data.items():
            if isinstance(v, dict):
                out_lines.append(f"{indent}- {k} (dict, keys: {len(v)})")
                dump_keys_recursively(v, level + 1, out_lines)
            elif isinstance(v, list):
                out_lines.append(f"{indent}- {k} (list, size: {len(v)})")
                if len(v) > 0:
                    out_lines.append(f"{indent}  [sample item type: {type(v[0]).__name__}]")
                    dump_keys_recursively(v[0], level + 2, out_lines)
            else:
                out_lines.append(f"{indent}- {k} (type: {type(v).__name__}, value: {str(v)[:150]})")
    elif isinstance(data, list):
        if len(data) > 0:
            out_lines.append(f"{indent}[list item type: {type(data[0]).__name__}]")
            dump_keys_recursively(data[0], level + 1, out_lines)
    return out_lines

def main():
    if not os.path.exists(JSON_FILE):
        return

    with open(JSON_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)

    out_lines = dump_keys_recursively(data)
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        f.write("\n".join(out_lines))
    print(f"Dumped structure to {OUTPUT_FILE}")

if __name__ == "__main__":
    main()
