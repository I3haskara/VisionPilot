import time
import argparse
import requests

DEFAULT_ENDPOINT = "http://127.0.0.1:8000/selection"


def send_coords_once(endpoint: str, x: float, y: float, verbose: bool = True):
    payload = {"x": float(x), "y": float(y)}
    try:
        r = requests.post(endpoint, json=payload, timeout=0.2)
        if verbose:
            print(f"→ sent x={x:.3f}, y={y:.3f} | status={r.status_code} | resp={r.json()}")
    except Exception as e:
        print(f"!! error sending x={x:.3f}, y={y:.3f}: {e}")


def demo_sequence(endpoint: str, delay: float):
    points = [
        (0.25, 0.40),
        (0.50, 0.50),
        (0.75, 0.40),
    ]
    for x, y in points:
        send_coords_once(endpoint, x, y)
        time.sleep(delay)


def main():
    parser = argparse.ArgumentParser(description="Send demo selection coordinates to VisionPilot FastAPI server.")
    parser.add_argument(
        "--endpoint",
        type=str,
        default=DEFAULT_ENDPOINT,
        help=f"Selection endpoint URL (default: {DEFAULT_ENDPOINT})",
    )
    parser.add_argument(
        "--mode",
        type=str,
        choices=["demo", "single"],
        default="demo",
        help="demo = sweep three points, single = send one coordinate",
    )
    parser.add_argument("--x", type=float, default=0.5, help="X coord (0–1) for single mode")
    parser.add_argument("--y", type=float, default=0.5, help="Y coord (0–1) for single mode")
    parser.add_argument("--delay", type=float, default=0.8, help="Delay between demo coords in seconds")

    args = parser.parse_args()

    if args.mode == "single":
        send_coords_once(args.endpoint, args.x, args.y)
    else:
        demo_sequence(args.endpoint, args.delay)


if __name__ == "__main__":
    main()
