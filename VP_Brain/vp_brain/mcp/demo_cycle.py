"""Simple demo cycle that posts segment changes to the Selection Server."""

# vp_brain/mcp/demo_cycle.py

import time
import requests

URL = "http://127.0.0.1:8000/selection"

# These must match your Unity segmentId fields on ARSegmentObjectGroup
SEQUENCE = ["cover", "page_1", "page_2", "page_3"]


def main():
    while True:
        for seg in SEQUENCE:
            print("Switch →", seg)
            try:
                resp = requests.post(
                    URL,
                    json={
                        "x": 0.5,
                        "y": 0.5,
                        "source": "demo",
                        "segment_id": seg,
                    },
                    timeout=2,
                )
                print("  status:", resp.status_code)
            except Exception as e:
                print("  ERROR sending selection:", e)

            # How long each “page” stays visible
            time.sleep(2)


if __name__ == "__main__":
    main()
