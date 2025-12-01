import requests
import time

coords = [(0.2, 0.3), (0.5, 0.5), (0.8, 0.4)]

for x, y in coords:
    resp = requests.post("http://127.0.0.1:8000/selection", json={"x": x, "y": y})
    print("sent", x, y, "->", resp.json())
    time.sleep(1)
