# Fotoparadies Order Status Checker

This script automates fetching order statuses from the **Fotoparadies / dm photo service** backend API (`spot.photoprintit.com`).

It reads order data from CSV files in an `orders/` folder, retrieves each order’s current status, and displays the results in clean tables grouped by file.  

I just made this because I was sick of manually checking the status of my orders on the Fotoparadies website all the time.

Maybe it will be useful for you too.

---

##  Features

- Reads all `.csv` files from a local `orders/` folder  
- Queries Fotoparadies API for real-time order status
- Displays results in clean, grouped tables

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
├── fotoparadies_status.py        # Main script
├── README.md                     # (this file)
│
├── orders/                       # Folder containing your CSV input files
│   ├── berlin_orders.csv
│   ├── munich_orders.csv
│   └── test_orders.csv
```

---

## Input CSV Format

Each CSV file in the `orders/` folder must contain **three columns**:

| Column Name    | Description                                        |
|----------------|----------------------------------------------------|
| `order_number` | Fotoparadies order number (e.g. 112344525)         | 
| `shop_number`  | dm shop number (e.g. 112344)                       |
| `Identifier`   | Any label or identifier you want (e.g. “Berlin_1”) |

**Note:** If you already have the full order number in the format `shop_number-order_number` (e.g., "112344-112344525"), you can put it directly in the `order_number` column. The script will automatically detect and use it without reconstructing it from the individual order and shop numbers.

### Example: `orders/test_orders.csv`
```csv
order_number,shop_number,Identifier
112344525,112344,Berlin_1
112344526,112344,Berlin_2
112344-112345,112344,Berlin_3
```

In the example above, the third row uses the full order number format directly.

---

## How to Run

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

---

## Example Output

```
Processing file: test_orders.csv
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
If you're working for dm or photoprintit, please don't sue me, this isn't gonna hurt you 🙂
