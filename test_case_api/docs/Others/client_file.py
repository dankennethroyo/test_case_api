import argparse
import json
import os
import sys
import requests
from pathlib import Path

DEFAULT_BASE_URL = "http://localhost:5000"

def send_file(file_path: str, base_url: str, model: str = None, output: str = None) -> int:
    file_path = Path(file_path)
    if not file_path.exists():
        print(f"Error: file not found: {file_path}", file=sys.stderr)
        return 2

    url = f"{base_url.rstrip('/')}/generate/file"
    files = {"file": (file_path.name, open(file_path, "rb"), "application/json")}
    data = {}
    if model:
        data["model"] = model

    try:
        resp = requests.post(url, files=files, data=data, timeout=300)
    except requests.exceptions.RequestException as e:
        print(f"Request failed: {e}", file=sys.stderr)
        return 3
    finally:
        files["file"][1].close()

    try:
        resp.raise_for_status()
    except requests.exceptions.HTTPError:
        print(f"Server returned status {resp.status_code}:\n{resp.text}", file=sys.stderr)
        return 4

    try:
        resp_json = resp.json()
    except ValueError:
        print("Response is not valid JSON", file=sys.stderr)
        return 5

    out_path = Path(output) if output else (file_path.with_suffix(".results.json"))
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(resp_json, f, indent=2, ensure_ascii=False)

    print(f"Success: results saved to {out_path}")
    return 0

def main():
    p = argparse.ArgumentParser(description="Upload requirements JSON to /generate/file and save results.")
    p.add_argument("file", help="Path to requirements JSON file (object, array, or {\"requirements\":[...]})")
    p.add_argument("--base-url", default=os.getenv("TESTCASE_API_URL", DEFAULT_BASE_URL),
                   help=f"API base URL (default: {DEFAULT_BASE_URL})")
    p.add_argument("--model", default=os.getenv("TESTCASE_MODEL"),
                   help="Optional model name to pass to the API (default: from TESTCASE_MODEL env var)")
    p.add_argument("--output", help="Output file path (defaults to <input>.results.json)")
    args = p.parse_args()

    exit_code = send_file(args.file, args.base_url, args.model, args.output)
    sys.exit(exit_code)

if __name__ == "__main__":
    main()