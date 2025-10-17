import os
import csv
import time
import json
import requests
from prettytable import PrettyTable

# === Configuration ===
ORDERS_DIR = "orders"  # folder containing CSV input files
BASE_URL = "https://spot.photoprintit.com/spotapi/orderInfo/order"
CONFIG_ID = "1320"
OUTPUT_FILE = "order_status_results.json"

HEADERS = {
    "Accept": "application/json, text/plain, */*",
    "Accept-Language": "en-US,en;q=0.9,de-DE;q=0.8,de;q=0.7",
    "User-Agent": (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/141.0.0.0 Safari/537.36"
    ),
    "Origin": "https://www.fotoparadies.de",
    "Referer": "https://www.fotoparadies.de/",
    "DNT": "1",
    "Connection": "keep-alive",
    "Sec-Fetch-Dest": "empty",
    "Sec-Fetch-Mode": "cors",
    "Sec-Fetch-Site": "cross-site",
}

REQUEST_DELAY = 0.6  # seconds between requests

# === Emoji mapping for order statuses ===
STATUS_EMOJIS = {
    "PROCESSING": "🚀",
    "wird gefertigt": "🚀",
    "In Produktion": "🚀",
    "Produktion": "🚀",
    "SHIPPED": "📦",
    "Versandt": "📦",
    "COMPLETED": "✅",
    "Abgeschlossen": "✅",
    "CANCELLED": "❌",
    "Storniert": "❌",
    "Fehler": "⚠️",
    "Unknown": "❓",
}

def add_status_emoji(status: str) -> str:
    """Attach an emoji to a status text."""
    for key, emoji in STATUS_EMOJIS.items():
        if key.lower() in status.lower():
            return f"{emoji} {status}"
    return f"❓ {status}"


def fetch_order_status(order_number: str, shop_number: str):
    """Fetch order status for a single order."""
    full_order_id = f"{shop_number}-{order_number}"
    params = {
        "config": CONFIG_ID,
        "fullOrderId": full_order_id,
    }
    try:
        resp = requests.get(BASE_URL, headers=HEADERS, params=params, timeout=10)
        resp.raise_for_status()
        data = resp.json()
        
        # Parse new response format
        status_text = data.get("summaryStateText", "")
        status_code = data.get("summaryStateCode", "")
        
        if not status_text:
            status_text = status_code or "Unknown"
        
        return add_status_emoji(status_text)
    except Exception as e:
        return f"⚠️ Error: {str(e)}"


def process_csv_file(file_path):
    """Read one CSV and fetch all order statuses."""
    results = []
    with open(file_path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            order = row["order_number"].strip()
            shop = row["shop_number"].strip()
            ident = row.get("Identifier", "").strip()

            status = fetch_order_status(order, shop)
            results.append({
                "order_number": order,
                "shop_number": shop,
                "Identifier": ident,
                "status": status
            })
        
            time.sleep(REQUEST_DELAY)
    return results


def main():
    if not os.path.exists(ORDERS_DIR):
        print(f"❌ Folder '{ORDERS_DIR}' not found.")
        return

    all_results = {}

    for filename in sorted(os.listdir(ORDERS_DIR)):
        if not filename.lower().endswith(".csv"):
            continue
        file_path = os.path.join(ORDERS_DIR, filename)
        print(f"\n Processing file: {filename}")
        file_results = process_csv_file(file_path)
        all_results[filename] = file_results

    # Print grouped tables
    print("\n================= ORDER STATUS SUMMARY =================")
    for filename, results in all_results.items():
        table = PrettyTable(["Order Number", "Shop Number", "Identifier", "Status"])
        for r in results:
            table.add_row([r["order_number"], r["shop_number"], r["Identifier"], r["status"]])
        print(f"\n=== {filename} ===")
        print(table)


if __name__ == "__main__":
    main()
