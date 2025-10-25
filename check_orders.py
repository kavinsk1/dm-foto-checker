"""Main script for checking Fotoparadies order statuses and downloading photos."""

import os
import csv
import time
import argparse
import requests
from pathlib import Path
from prettytable import PrettyTable
from downloader import download_photos

# === Configuration ===
ORDERS_DIR = "orders"  # folder containing CSV input files
BASE_URL = "https://spot.photoprintit.com/spotapi/orderInfo/order"
CONFIG_ID = "1320"

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
DOWNLOADS_DIR = "downloads"  # folder for downloaded photos

# === Emoji mapping for order statuses ===
STATUS_EMOJIS = {
    "PROCESSING": "🏭",
    "SHIPPED": "📦",
    "DELIVERED": "✅",
    "CANCELLED": "❌",
    "ERROR": "⚠️",
    "Unknown": "❓",
}

def add_status_emoji(status_code: str, status_text: str) -> str:
    """
    Attach an emoji to a status text based on the status code.
    
    Args:
        status_code: Status code from API (e.g., "DELIVERED")
        status_text: Human-readable status text
        
    Returns:
        str: Formatted status with emoji prefix
    """
    for key, emoji in STATUS_EMOJIS.items():
        if key.lower() in status_code.lower():
            return f"{emoji} {status_text}"
    
    # Log unmapped status codes for debugging
    print(f"⚠️  Unmapped status_code: '{status_code}'")
    return f"❓ {status_text}"


def is_ready_for_pickup(status_code: str) -> bool:
    """
    Check if order status indicates ready for pickup.
    
    Args:
        status_code: Status code from API
        
    Returns:
        bool: True if status is DELIVERED, False otherwise
    """
    return status_code.upper() == "DELIVERED"


def fetch_order_status(order_number: str, shop_number: str):
    """
    Fetch order status for a single order from Fotoparadies API.
    
    Args:
        order_number: Order number (e.g., "050842" or "541032-050842")
        shop_number: Shop number (e.g., "541032")
        
    Returns:
        tuple: (status_code, formatted_status) where status_code is the raw API code
               and formatted_status includes emoji and text
    """
    # Check if order_number is already in full format (e.g., "123456-123456")
    if "-" in order_number and len(order_number.replace("-", "")) == 12:
        full_order_id = order_number
    else:
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
        
        formatted_status = add_status_emoji(status_code, status_text)
        return status_code, formatted_status
    except Exception as e:
        return "", f"⚠️ Error: {str(e)}"


def process_csv_file(file_path, enable_download=False):
    """
    Process a CSV file to check order statuses and optionally download photos.
    
    Args:
        file_path: Path to the CSV file
        enable_download: Whether to download photos for ready orders
        
    Returns:
        list: List of dictionaries containing order information and results
    """
    results = []
    with open(file_path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            order = row["order_number"].strip()
            shop = row["shop_number"].strip()
            ident = (row.get("identifier") or "").strip()
            secure_id = (row.get("secure_id") or "").strip().upper()
            cewe_order_id = (row.get("cewe_order_id") or "").strip()
            csv_output_path = (row.get("output_path") or "").strip()

            status_code, status = fetch_order_status(order, shop)
            
            # Determine if we should download
            should_download = (
                enable_download and 
                secure_id and 
                is_ready_for_pickup(status_code)
            )
            
            download_status = ""
            if should_download:
                # Determine output path: CSV column > downloads/{identifier}
                if csv_output_path:
                    output_path = Path(csv_output_path).resolve()
                elif ident:
                    # Create folder named after identifier (with spaces replaced by underscores) in downloads/
                    safe_ident = ident.replace(" ", "_")
                    output_path = Path(DOWNLOADS_DIR) / safe_ident
                else:
                    # Fallback to downloads directory
                    output_path = Path(DOWNLOADS_DIR)
                
                # Check if already downloaded (folder exists and has files)
                if output_path.exists() and any(output_path.iterdir()):
                    download_status = "✅ Already downloaded"
                else:
                    # Create output directory if it doesn't exist
                    try:
                        output_path.mkdir(parents=True, exist_ok=True)
                    except Exception as e:
                        print(f"  ❌ Could not create output folder: {output_path}. Details: {e}")
                        download_status = "❌ Folder creation failed"
                        results.append({
                            "order_number": order,
                            "shop_number": shop,
                            "identifier": ident,
                            "secure_id": secure_id,
                            "cewe_order_id": cewe_order_id,
                            "output_path": csv_output_path,
                            "status": status,
                            "download_status": download_status
                        })
                        time.sleep(REQUEST_DELAY)
                        continue
                    
                    # Use cewe_order_id if provided, otherwise use the regular order
                    download_order_id = cewe_order_id if cewe_order_id else order
                    if "-" not in download_order_id:
                        download_order_id = f"{shop}-{download_order_id}"
                    
                    print(f"\n📥 Downloading photos for {ident} (Order: {download_order_id})...")
                    print(f"  📁 Output folder: {output_path}")
                    if cewe_order_id:
                        print(f"  Using CEWE order ID: {cewe_order_id}")
                    
                    success = download_photos(download_order_id, secure_id, output_path)
                    download_status = "✅ Downloaded" if success else "❌ Download failed"
            
            results.append({
                "order_number": order,
                "shop_number": shop,
                "identifier": ident,
                "secure_id": secure_id,
                "cewe_order_id": cewe_order_id,
                "output_path": csv_output_path,
                "status": status,
                "download_status": download_status
            })
        
            time.sleep(REQUEST_DELAY)
    return results


def main():
    parser = argparse.ArgumentParser(
        description="Check Fotoparadies order statuses and optionally download photos.",
        formatter_class=argparse.RawTextHelpFormatter
    )
    parser.add_argument(
        '--download',
        action='store_true',
        help="Automatically download photos for orders that are ready for pickup and have a secure_id."
    )
    
    args = parser.parse_args()
    
    if not os.path.exists(ORDERS_DIR):
        print(f"❌ Folder '{ORDERS_DIR}' not found.")
        return

    # Ensure downloads directory exists if download is enabled
    if args.download:
        downloads_dir = Path(DOWNLOADS_DIR)
        if not downloads_dir.exists():
            try:
                downloads_dir.mkdir(parents=True, exist_ok=True)
                print(f"📁 Created download folder: {downloads_dir}")
            except Exception as e:
                print(f"❌ Could not create download folder: {downloads_dir}. Details: {e}")
                return

    all_results = {}

    for filename in sorted(os.listdir(ORDERS_DIR)):
        if not filename.lower().endswith(".csv"):
            continue
        # Skip template file
        if filename.lower() == "orders_template.csv":
            continue
        file_path = os.path.join(ORDERS_DIR, filename)
        print(f"\n Processing file: {filename}")
        file_results = process_csv_file(file_path, args.download)
        all_results[filename] = file_results

    # Print grouped tables
    print("\n================= ORDER STATUS SUMMARY =================")
    for filename, results in all_results.items():
        # Determine columns based on whether downloads were attempted
        has_downloads = any(r.get("download_status") for r in results)
        has_secure_ids = any(r.get("secure_id") for r in results)
        has_cewe_ids = any(r.get("cewe_order_id") for r in results)
        has_output_paths = any(r.get("output_path") for r in results)
        
        columns = ["Order Number", "Shop Number", "Identifier"]
        if has_secure_ids:
            columns.append("Secure ID")
        if has_cewe_ids:
            columns.append("CEWE Order ID")
        if has_output_paths:
            columns.append("Output Path")
        columns.append("Status")
        if has_downloads:
            columns.append("Download")
        
        table = PrettyTable(columns)
        for r in results:
            row = [r["order_number"], r["shop_number"], r["identifier"]]
            if has_secure_ids:
                row.append(r.get("secure_id", ""))
            if has_cewe_ids:
                row.append(r.get("cewe_order_id", ""))
            if has_output_paths:
                row.append(r.get("output_path", ""))
            row.append(r["status"])
            if has_downloads:
                row.append(r.get("download_status", ""))
            table.add_row(row)
        print(f"\n=== {filename} ===")
        print(table)


if __name__ == "__main__":
    main()
