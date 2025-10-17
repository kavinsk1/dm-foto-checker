# Fotoparadies Order Status Checker

This script automates fetching order statuses from the **Fotoparadies / dm photo service** backend API (`spot.photoprintit.com`).

It reads order data from CSV files in an `orders/` folder, retrieves each order’s current status, and displays the results in clean tables grouped by file.  

I just made this because I was sick of manually checking the status of my orders on the Fotoparadies website all the time.

Maybe it will be useful for you too.

---

##  Features

- Reads all `.csv` files from a local `orders/` folder  
- Supports the input format:
  ```
  order_number,shop_number,Identifier
  ```
- Queries Fotoparadies API (`spot.photoprintit.com/spotapi/orderInfo/forShop`)
- Prints grouped tables (one per CSV file)

---

## Requirements

- **Python 3.8+**
- **Poetry** (recommended) or pip

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
├── fotoparadies_status.py        # Main script
├── README.md                     # (this file)
│
├── orders/                       # Folder containing your CSV input files
│   ├── berlin_orders.csv
│   ├── munich_orders.csv
│   └── test_orders.csv
│
└── order_status_results.json     # Output generated after running the script
```

---

## Input CSV Format

Each CSV file in the `orders/` folder must contain **three columns**:

| Column Name    | Description                                        |
|----------------|----------------------------------------------------|
| `order_number` | Fotoparadies order number (e.g. 112344525)         |
| `shop_number`  | dm shop number (e.g. 112344)                       |
| `Identifier`   | Any label or identifier you want (e.g. “Berlin_1”) |

### Example: `orders/test_orders.csv`
```csv
order_number,shop_number,Identifier
112344525,112344,Berlin_1
112344526,112344,Berlin_2
112344527,112344,Berlin_3
```

---

## ▶️ How to Run

### With Poetry

```bash
poetry run check-orders
```

### With Python directly

```bash
python check_orders.py
```

The script will:

1. Look inside the `orders/` folder.
2. Process all `.csv` files it finds.
3. Fetch each order’s status from Fotoparadies.
4. Display tables of results grouped by file.

---

## 📊 Example Output

```
📂 Processing file: test_orders.csv
Fetched 112344525 (Berlin_1): In Produktion
Fetched 112344526 (Berlin_2): Versandt
Fetched 112344527 (Berlin_3): Abgeschlossen

================= 📋 ORDER STATUS SUMMARY =================

=== test_orders.csv ===
+--------------+-------------+------------+-----------------+
| Order Number | Shop Number | Identifier |      Status     |
+--------------+-------------+------------+-----------------+
| 112344525    | 112344      | Berlin_1   | In Produktion   |
| 112344526    | 112344      | Berlin_2   | Versandt        |
| 112344527    | 112344      | Berlin_3   | Abgeschlossen   |
+--------------+-------------+------------+-----------------+

💾 Results saved to 'order_status_results.json'
```

---


## Configuration

You can adjust a few constants inside the script:

| Variable        | Description                  | Default                                                   |
|-----------------|------------------------------------------------|-----------------------------------------------------------|
| `ORDERS_DIR`    | Folder where CSVs are stored                   | `"orders"`                                                |
| `BASE_URL`      | API endpoint                                   | `https://spot.photoprintit.com/spotapi/orderInfo/forShop` |
| `CONFIG_ID`     | API config value (do not change unless needed) | `1320`                                                    |
| `REQUEST_DELAY` | Delay between requests in seconds              | `0.6`                                                     |


## License

This project is provided “as-is” for personal use.  
It’s not affiliated with or endorsed by **Fotoparadies** or **dm**.
