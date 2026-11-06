# MediQuick - Pharmacy Billing System

MediQuick is a modular Python 3 console application designed for campus health store counter computers. It provides separated workflows for **Staff** (inventory management) and **Customers** (browsing, shopping cart, and order checkout with 12% flat GST), backed by a persistent CSV storage engine.

---

## Architecture & Project Structure

The project follows clean Object-Oriented Programming (OOP) and Single Responsibility principles, maintaining one class per file:

```text
mediquickv2-pharmacy-billing-system-fastapi/
│
├── app/
│   ├── exceptions/
│   │   ├── __init__.py
│   │   └── insufficient_stock_error.py  # Custom InsufficientStockError exception
│   ├── models/
│   │   ├── __init__.py
│   │   ├── medicine.py                  # Medicine entity (attributes, validation, reduce_stock)
│   │   └── cart.py                      # Cart entity (item aggregation, totals, 12% GST)
│   ├── pharmacy.py                      # Pharmacy catalogue & CSV persistence manager
│   ├── ui.py                            # Reusable input helpers, CLI menus & screen flows
│   └── main.py                          # Application entry point
│
├── tests/
│   └── test_calculations.py             # Deterministic tests (subtotal, GST, totals, rounding)
│
├── medicines.csv                        # Persistent CSV data storage for medicines
└── README.md
```

---

## Behind the Scenes: How It Works

### 1. Console UI & Interaction Flow

The console interface operates on a stateful, non-terminating interaction loop:

- **State & Session Isolation**:
  When the application starts, `main_menu()` instantiates a `Cart` object and an order counter dictionary `{"order_no": 1001}`. These remain persistent throughout the session so customers can browse, view cart, and place orders across multiple customer menu visits.
- **Hierarchical Routing**:
  - **Main Menu**: Routes to either Staff Flow, Customer Flow, or exits cleanly.
  - **Staff Flow**: Protected by password authentication (`admin123`). If incorrect, the user is immediately routed back to the main menu without retries.
  - **Customer Flow**: Exposes menu actions (View menu, Search, Add to cart, View cart, Place order, Back).
- **Input Validation & Crash Prevention (FR11)**:
  Instead of wrapping raw `input()` in fragmented `try...except` blocks across menus, the UI utilizes reusable input validation loops:
  - `prompt_int(msg, min_val)`: Traps `ValueError` when non-numeric input is supplied, displays `"Please enter a whole number."`, and re-prompts until valid.
  - `prompt_float(msg)`: Traps `ValueError`, validates positive price values, and re-prompts on errors.
  - `prompt_yes_no(msg)`: Validates that answers are strictly `'y'` or `'n'` (case-insensitive); re-prompts on any other entry.
  - `prompt_str(msg)`: Prevents empty or whitespace-only submissions.
  - `KeyboardInterrupt` / `EOFError`: Caught gracefully at the entry point to exit cleanly without dumping stack traces.

---

### 2. Business Logic & Domain Models

- **`Medicine` (`app/models/medicine.py`)**:
  - Represents an inventory item (`code`, `name`, `category`, `price`, `stock`, `rx`).
  - Enforces domain constraints: item price must be $> 0$, stock must be $\ge 0$, and `rx` must be `'Y'` or `'N'`.
  - Implements `reduce_stock(quantity)`: verifies sufficient stock is available; if not, it raises `InsufficientStockError`.
- **`Cart` (`app/models/cart.py`)**:
  - Stores items internally as `{code: {"medicine": Medicine, "quantity": int}}`.
  - Adding the same item repeatedly increments the quantity of that existing line rather than duplicating lines.
  - Adding items checks that the total requested quantity in the cart does not exceed available stock.
  - Calculates subtotal (`sum(price * quantity)`), flat 12% GST (`round(subtotal * 0.12, 2)`), and grand total (`round(subtotal + gst, 2)`), with rounding strictly capped at 2 decimal places.
- **`InsufficientStockError` (`app/exceptions/insufficient_stock_error.py`)**:
  - Custom domain exception raised when an order or cart request exceeds available stock.
  - Caught in `customer_add()` and `customer_order()` in `ui.py` to notify the user with a friendly warning rather than crashing.

---

### 3. Data Persistence & File Handling Logic

MediQuick persists its catalogue to `medicines.csv` in the root project directory:

```csv
code,name,category,price,stock,rx
T01,Paracetamol 500mg,Tablets,25,60,N
T02,Amoxicillin 250mg,Tablets,85,8,Y
S01,Cough Syrup 100ml,Syrups,70,20,N
F01,Antiseptic Cream 20g,First Aid,45,0,N
F02,Cotton Roll 100g,First Aid,30,15,N
W01,Vitamin C (30 tabs),Wellness,120,25,N
```

#### File Loading Flow (`load_from_csv`):
1. On startup, `Pharmacy.__init__()` invokes `self.load_from_csv()`.
2. Attempts to open `medicines.csv` using `csv.DictReader` with UTF-8 encoding.
3. If `medicines.csv` is missing, Python raises `FileNotFoundError`. The exception is caught, the pharmacy starts with an empty dictionary `{}` without crashing, and a warning is printed to the user.
4. Each row is converted into a `Medicine` instance and cached in `self.medicines` dictionary keyed by uppercase item code for $O(1)$ lookups.

#### File Saving Flow (`save_to_csv`):
Persistence is executed **immediately after every state-changing event**:
1. **Adding a Medicine**: Saved as soon as staff completes the `Add Medicine` form.
2. **Updating a Medicine**: Saved immediately after new price or stock is set.
3. **Placing an Order**: When customer checks out:
   - In-memory stock is verified for all items in the cart.
   - `med.reduce_stock(qty)` decreases the inventory count.
   - `pharmacy.save_to_csv()` rewrites the updated stock counts to `medicines.csv`.
   - The formatted receipt is printed, and the cart is emptied.
- **File Safety**: Uses the Python context manager `with open(..., mode="w", newline="", encoding="utf-8") as f:` to guarantee proper file closing and descriptor flushing even if an unexpected interruption occurs.

---

## How to Run

From the project root directory:

```bash
python -m app.main
```

---

## How to Test

Deterministic calculation scenarios (line totals, cart subtotal, 12% GST calculation, grand total, currency rounding, repeated item additions, item removals, and stock reductions) are verified via `pytest`:

```bash
pytest
```
