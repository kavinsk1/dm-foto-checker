"""
Photo downloader module for dm-foto-checker.
Handles downloading and extracting photos from CEWE API.
"""

import sys
import time
import zipfile
import requests
from pathlib import Path


# === Download API Configuration ===
# Note: The 'aak' (API Access Key) may expire. If downloads fail with 403/404 errors,
# you'll need to update this key by inspecting network requests in your browser.
CEWE_DYNAMIC_PARAMS = {
    'aak': '8ccc7bec8f9899140873db6b01254f35cc3a04ed',
    'clientVersion': '2.116.1-20251022-gd981d25'
}

DOWNLOAD_BASE_API_URL = 'https://api.cewe-myphotos.com/api/imageCD'


def download_file(url, output_path, filename):
    """
    Download a file with progress indicator and auto-extract if it's a ZIP.
    
    Args:
        url: Full URL to download from
        output_path: Path object for the output directory
        filename: Name of the file to save
        
    Returns:
        bool: True if download and extraction succeeded, False otherwise
    """
    
    full_path = output_path / filename
    
    print(f"  -> Starting download from: {url}")
    print(f"  -> Saving to: {full_path}")

    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/141.0.0.0 Safari/537.36',
            'Referer': 'https://www.fotoparadies.de/' if 'fotoparadies' in url else 'https://www.cewe-myphotos.com/',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7'
        }
        
        response = requests.get(url, headers=headers, stream=True, timeout=300)
        response.raise_for_status()

    except requests.exceptions.RequestException as e:
        print(f"  [ERROR] Could not download file. Details: {e}")
        return False

    total_size = int(response.headers.get('content-length', 0))
    bytes_downloaded = 0
    
    print(f"  -> File size: {total_size / (1024 * 1024):.2f} MB")

    try:
        with open(full_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)
                    bytes_downloaded += len(chunk)
                    percent = (bytes_downloaded / total_size) * 100 if total_size > 0 else 0
                    sys.stdout.write(f"\r  Downloaded: {bytes_downloaded / (1024 * 1024):.2f} MB / {total_size / (1024 * 1024):.2f} MB ({percent:.1f}%)")
                    sys.stdout.flush()
        
        print(f"\n  [SUCCESS] Download complete! File saved to: {full_path}")
        
        # Auto-unzip the downloaded file
        try:
            print(f"  -> Extracting ZIP file...")
            with zipfile.ZipFile(full_path, 'r') as zip_ref:
                zip_ref.extractall(output_path)
            print(f"  [SUCCESS] Extracted to: {output_path}")
            
            # Delete the ZIP file after extraction
            full_path.unlink()
            print(f"  -> Removed ZIP file")
        except zipfile.BadZipFile:
            print(f"  [WARNING] File is not a valid ZIP archive, keeping as-is")
        except Exception as e:
            print(f"  [WARNING] Could not extract ZIP file: {e}")
        
        return True
        
    except IOError as e:
        print(f"\n  [ERROR] Could not write to output directory: {output_path}")
        print(f"  Details: {e}")
        return False


def download_photos(order_id, secure_id, output_folder):
    """
    Download photos from CEWE API.
    
    Args:
        order_id: Full order ID (e.g., "541032-050842")
        secure_id: Secure ID from pickup envelope (e.g., "ZTVLYEQ5")
        output_folder: Path object for the output directory
        
    Returns:
        bool: True if download succeeded, False otherwise
    """
    query_params = {
        'aak': CEWE_DYNAMIC_PARAMS['aak'],
        'clientVersion': CEWE_DYNAMIC_PARAMS['clientVersion']
    }
    
    url = f"{DOWNLOAD_BASE_API_URL}/{order_id}/{secure_id}/download"
    req = requests.Request('GET', url, params=query_params).prepare()

    filename = f"photos_{order_id}.zip"
    return download_file(req.url, output_folder, filename)
