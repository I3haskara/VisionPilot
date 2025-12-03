import time
import requests

SERVER_URL = "http://127.0.0.1:8000/selection"

# A small demo path in normalized coordinates (0–1)
DEMO_POINTS = [
    (0.2, 0.3),
    (0.5, 0.5),
    (0.8, 0.4),
]


def send_point(x: float, y: float):
    payload = {"x": x, "y": y}
    resp = requests.post(SERVER_URL, json=payload, timeout=0.5)
    resp.raise_for_status()
    print(f"Sent: {payload}  ->  {resp.json()}")


def main():
    print(f"Sending demo selection path to {SERVER_URL}")
    for x, y in DEMO_POINTS:
        send_point(x, y)
        time.sleep(0.5)

    print("Done.")


if __name__ == "__main__":
    main()
