# Fotoparadies Order Status Checker

This script automates fetching order statuses from the **Fotoparadies / dm photo service** backend API (`spot.photoprintit.com`).

It reads order data from CSV files in an `orders/` folder, retrieves each order’s current status, and displays the results in clean tables grouped by file.  

I just made this because I was sick of manually checking the status of my orders on the Fotoparadies website all the time.

Maybe it will be useful for you too.

---

##  Features

- Queries Fotoparadies API for real-time order status
- **Automatically downloads and extracts digital photos** when orders are ready for pickup (with `--download` flag)

---

## Requirements

- **Python**
- **Poetry** 

### Installation with Poetry (Recommended)

```bash
# Install dependencies
poetry install

# Run the script
poetry run check-orders
```

### Installation with pip

```bash
pip install requests prettytable
```

---

## Folder Structure

```
project_root/
│
├── check_orders.py               # Main script
├── downloader.py                 # Photo download module
├── README.md                     # (this file)
│
├── orders/                       # Folder containing your CSV input files
│   ├── berlin_orders.csv
│   ├── munich_orders.csv
│   └── test_orders.csv
│
├── downloads/                    # Downloaded and extracted photos
│   ├── berlin_1/
│   └── munich_1/
```

---

## Input CSV Format

Each CSV file in the `orders/` folder must contain **three required columns** and **up to three optional columns**:

| Column Name      | Required | Description                                                                             |
|------------------|----------|-----------------------------------------------------------------------------------------|
| `order_number`   | Yes      | Fotoparadies order number (e.g. 112344525, right on the envelope strip)                 | 
| `shop_number`    | Yes      | dm shop number (e.g. 112344, left on the envelope strip)                                |
| `identifier`     | Yes      | Any label or identifier you want (e.g. "Berlin_1")                                      |
| `secure_id`      | Optional | Secure ID from the pickup envelope (e.g. "PREHU6R6") - required for downloads           |
| `cewe_order_id`  | Optional | Alternative CEWE order ID if different from the main order number                       |
| `output_path`    | Optional | Custom download path (e.g. "~/Pictures/Norway"). If empty, uses `downloads/{identifier}`|

**Notes:** 
- If you already have the full order number in the format `shop_number-order_number` (e.g., "112344-112344525"), you can put it directly in the `order_number` column. The script will automatically detect and use it.
- Add the `secure_id` after picking up your photos from the store - it's printed on the sheet in the envelope. Case doesn't matter (automatically converted to uppercase).
- The `cewe_order_id` is only needed if the download requires a different order ID than the one used for status checking.
  (sometimes CEWE assignes your order an internal ORDER-ID during development, see the sheet in the envelope for that ID)
- **Download folder priority**: `output_path` (if specified) → `downloads/{identifier}`

### Example: `orders/order_template.csv`


## How to Run

### Basic Usage (Check Status Only)

```bash
# Install dependencies
poetry install

# Run the checker
poetry run check-orders
```

The script will:

1. Look inside the `orders/` folder
2. Process all `.csv` files it finds
3. Fetch each order's status from Fotoparadies
4. Display tables of results grouped by file
5. Download photos for all ready orders when --download flag is used

### Download Photos Automatically

When your orders are ready for pickup and you've added the `secure_id` (and the cewe_order_id if needed)  to your CSV:

```bash
# Download photos for all ready orders with secure_id
poetry run check-orders --download
```

---

## Configuration

You can adjust a few constants inside the script:

| Variable        | Description                  | Default                                                   |
|-----------------|------------------------------------------------|-----------------------------------------------------------|
| `ORDERS_DIR`    | Folder where CSVs are stored                   | `"orders"`                                                |
| `DOWNLOADS_DIR` | Default folder for downloaded photos           | `"downloads"`                                             |
| `BASE_URL`      | API endpoint for status checks                 | `https://spot.photoprintit.com/spotapi/orderInfo/order`   |
| `CONFIG_ID`     | API config value (do not change unless needed) | `1320`                                                    |
| `REQUEST_DELAY` | Delay between requests in seconds              | `0.6`                                                     |

### Download API Keys

The download functionality uses dynamic API keys (`aak`) that may expire. If downloads fail with 403/404 errors, you'll need to update the keys in the script:

1. Open the CEWE/Fotoparadies website in your browser
2. Open Developer Tools (F12) → Network tab
3. Manually initiate a download
4. Find the download request and copy the `aak` parameter
5. Update `CEWE_DYNAMIC_PARAMS['aak']` in `downloader.py`

### CEWE Order ID

Sometimes the order ID used for downloading differs from the order ID used for status checks. In these cases:
- Add the download-specific order ID to the `cewe_order_id` column
- The script will use this ID for the download API call
- Leave empty if the order IDs are the same


## License

This project is provided "as-is" for personal use.  
It's not affiliated with or endorsed by **Fotoparadies** or **dm**.  
If you're working for dm or CEWE, please don't sue me, this isn't gonna hurt you 🙂
