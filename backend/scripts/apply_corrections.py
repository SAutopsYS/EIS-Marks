"""
POST every record from corrections.json to the corrections API.

Usage (server must already be running):
    python backend/scripts/apply_corrections.py
"""

import json
import sys
from pathlib import Path

import requests

DEFAULT_URL = 'http://127.0.0.1:8000/api/marks/corrections/'
DEFAULT_JSON = Path(__file__).resolve().parents[2] / 'data' / 'corrections.json'


def main():
    api_url = sys.argv[1] if len(sys.argv) > 1 else DEFAULT_URL
    json_path = Path(sys.argv[2]) if len(sys.argv) > 2 else DEFAULT_JSON

    with open(json_path, encoding='utf-8') as handle:
        corrections = json.load(handle)

    ok_count = 0
    fail_count = 0

    for correction in corrections:
        response = requests.post(api_url, json=correction, timeout=10)
        if response.status_code == 200:
            ok_count += 1
            print(f'OK  {correction} -> {response.status_code}')
        else:
            fail_count += 1
            print(
                f'FAIL {correction} -> {response.status_code} {response.text}'
            )

    print(f'Done: ok={ok_count} fail={fail_count}')


if __name__ == '__main__':
    main()
