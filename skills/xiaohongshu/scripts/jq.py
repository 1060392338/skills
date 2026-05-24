#!/usr/bin/env python3
"""Simple jq replacement for basic JSON parsing"""

import json
import sys

def main():
    if len(sys.argv) < 2:
        print("Usage: jq.py <json_string>")
        sys.exit(1)
    
    # Simple implementation: just print the JSON in pretty format
    try:
        data = json.loads(sys.argv[1])
        print(json.dumps(data, indent=2, ensure_ascii=False))
    except json.JSONDecodeError as e:
        print(f"Invalid JSON: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()
