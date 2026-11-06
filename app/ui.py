"""MediQuick console UI and menu flows."""

from app.exceptions.insufficient_stock_error import InsufficientStockError
from app.models.cart import Cart
from app.models.medicine import Medicine
from app.pharmacy import Pharmacy


# --- Input Helper Functions (FR11) ---

def prompt_str(msg):
    """Prompt until non-blank string is provided."""
    while True:
        val = input(msg).strip()
        if val:
            return val
        print("Input cannot be blank. Please try again.")


def prompt_int(msg, min_val=None):
    """Prompt for a whole number, handling ValueError and bounds."""
    while True:
        val = input(msg).strip()
        if not val:
            print("Input cannot be blank. Please enter a whole number.")
            continue
        try:
            num = int(val)
            if min_val is not None and num < min_val:
                print(f"Value must be at least {min_val}.")
                continue
            return num
        except ValueError:
            print("Please enter a whole number.")


def prompt_float(msg):
    """Prompt for a valid price, handling ValueError and ensuring positive amount."""
    while True:
        val = input(msg).strip()
        if not val:
            print("Input cannot be blank. Please enter a valid price.")
            continue
        try:
            num = float(val)
            if num <= 0:
                print("Price must be greater than zero.")
                continue
            return round(num, 2)
        except ValueError:
            print("Please enter a valid price.")


def prompt_yes_no(msg):
    """Prompt for y/n response and re-ask on any other input."""
    while True:
        ans = input(msg).strip().lower()
        if ans in ("y", "n"):
            return ans == "y"
        print("Please enter 'y' or 'n'.")


def display_medicines(medicines):
    """Display medicine list with zero stock shown as Out of stock (FR5)."""
    if not medicines:
        print("No medicines found.")
        return
    print("-" * 72)
    print(f"{'Code':<6} {'Name':<24} {'Category':<14} {'Price':<10} {'Stock':<12} {'Rx':<4}")
    print("-" * 72)
    for m in medicines:
        stock_str = "Out of stock" if m.is_out_of_stock() else str(m.stock)
        print(f"{m.code:<6} {m.name:<24} {m.category:<14} {m.price:<10.2f} {stock_str:<12} {m.rx:<4}")
    print("-" * 72)


# --- Staff Flow (FR2, FR3, FR4, FR5) ---

def staff_view(pharmacy: Pharmacy):
    """Display full medicine inventory."""
    print("\n--- Medicine Inventory ---")
    display_medicines(pharmacy.get_all_medicines())


def staff_add(pharmacy: Pharmacy):
    """Add a new medicine with unique code and valid details (FR3)."""
    print("\n--- Add Medicine ---")
    while True:
        code = prompt_str("Item code: ").upper()
        if pharmacy.get_medicine(code):
            print(f"Item code '{code}' already exists. Choose a unique code.")
        else:
            break

    name = prompt_str("Name: ")
    print("Categories: Tablets, Syrups, First Aid, Wellness")
    category = prompt_str("Category: ")
    price = prompt_float("Price: ")
    stock = prompt_int("Stock: ", min_val=0)
    rx = "Y" if prompt_yes_no("Requires prescription? (y/n): ") else "N"

    pharmacy.add_medicine(Medicine(code, name, category, price, stock, rx))
    print(f"Added {name} ({code}) successfully.")


def staff_update(pharmacy: Pharmacy):
    """Update price and/or stock of an existing medicine (FR4)."""
    print("\n--- Update Medicine ---")
    code = prompt_str("Item code: ").upper()
    med = pharmacy.get_medicine(code)
    if not med:
        print(f"Medicine '{code}' not found.")
        return

    print(f"Current {med.name} - Price: {med.price:.2f}, Stock: {med.stock}")
    if prompt_yes_no("Update price? (y/n): "):
        med.price = prompt_float("New price: ")
    if prompt_yes_no("Update stock? (y/n): "):
        med.stock = prompt_int("New stock: ", min_val=0)

    pharmacy.save_to_csv()
    print("Medicine updated successfully.")


def staff_menu(pharmacy: Pharmacy):
    """Display staff options and route choices."""
    while True:
        print("\n--- Staff Menu ---")
        print("1. View medicines")
        print("2. Add medicine")
        print("3. Update medicine")
        print("4. Back")
        choice = input("Enter choice: ").strip()
        if choice == "1":
            staff_view(pharmacy)
        elif choice == "2":
            staff_add(pharmacy)
        elif choice == "3":
            staff_update(pharmacy)
        elif choice == "4":
            break
        else:
            print("Invalid choice. Please choose 1-4.")


# --- Customer Flow (FR6, FR7, FR8, FR9) ---

def customer_view(pharmacy: Pharmacy):
    """View medicine list for customers."""
    print("\n--- Available Medicines ---")
    display_medicines(pharmacy.get_all_medicines())


def customer_search(pharmacy: Pharmacy):
    """Search medicines by substring match ignoring case (FR6)."""
    term = prompt_str("Search: ")
    results = pharmacy.search_by_name(term)
    if results:
        print(f"Results for '{term}':")
        display_medicines(results)
    else:
        print(f"No medicines found matching '{term}'.")


def customer_add(pharmacy: Pharmacy, cart: Cart):
    """Add item to cart with stock and prescription checks (FR7)."""
    code = prompt_str("Item code: ").upper()
    med = pharmacy.get_medicine(code)
    if not med:
        print(f"Medicine '{code}' not found.")
        return
    if med.is_out_of_stock():
        print(f"Sorry, {med.name} is out of stock.")
        return

    qty = prompt_int("Quantity: ", min_val=1)
    if med.rx == "Y":
        print(f"{med.code} is prescription-only.")
        if not prompt_yes_no("Do you have a valid prescription? (y/n): "):
            print(f"Sorry, a prescription is required for {med.name}.")
            return

    try:
        cart.add(med, qty)
        print(f"Added {qty} x {med.name} to your cart.")
    except InsufficientStockError as e:
        print(f"Insufficient stock: {e}")


def customer_cart(cart: Cart):
    """View cart items, subtotal, and optionally remove an item (FR8)."""
    if cart.is_empty():
        print("\nYour cart is empty.")
        return

    print("\n--- Your Cart ---")
    for code, item in cart.items.items():
        m = item["medicine"]
        q = item["quantity"]
        print(f"{m.name:<22} {q} x {m.price:.2f} = {round(q * m.price, 2):.2f}")
    print(f"Subtotal: {cart.calculate_subtotal():.2f}")

    if prompt_yes_no("Do you want to remove an item? (y/n): "):
        rem_code = prompt_str("Item code to remove: ").upper()
        if cart.remove(rem_code):
            print(f"Removed {rem_code} from cart.")
        else:
            print(f"Item {rem_code} not in cart.")


def customer_order(pharmacy: Pharmacy, cart: Cart, state: dict):
    """Finalize order, reduce stock, persist to CSV, and print receipt (FR9, FR10)."""
    if cart.is_empty():
        print("\nYour cart is empty. Nothing to place.")
        return

    try:
        for item in cart.items.values():
            item["medicine"].reduce_stock(item["quantity"])
    except InsufficientStockError as e:
        print(f"Order failed due to stock change: {e}")
        return

    pharmacy.save_to_csv()
    subtotal, gst, grand_total = cart.calculate_totals()
    order_no = state["order_no"]

    print()
    print("------ MediQuick Bill ------")
    print(f"Order No: {order_no}")
    for item in cart.items.values():
        m = item["medicine"]
        q = item["quantity"]
        line_total = round(m.price * q, 2)
        qty_price = f"{q} x {m.price:.2f}"
        print(f"{m.name:<22} {qty_price:<15} {line_total:>8.2f}")
    print("-" * 46)
    print(f"{'Subtotal':<37} {subtotal:>9.2f}")
    print(f"{'GST (12%)':<37} {gst:>9.2f}")
    print("-" * 46)
    print(f"{'Grand Total':<37} {grand_total:>9.2f}")
    print("-" * 46)
    print("Thank you! Collect at the counter.\n")

    state["order_no"] += 1
    cart.clear()


def customer_menu(pharmacy: Pharmacy, cart: Cart, state: dict):
    """Display customer menu and route choices."""
    while True:
        print("\n--- Customer Menu ---")
        print("1. View menu   2. Search   3. Add to cart")
        print("4. View cart   5. Place order   6. Back")
        choice = input("Enter choice: ").strip()
        if choice == "1":
            customer_view(pharmacy)
        elif choice == "2":
            customer_search(pharmacy)
        elif choice == "3":
            customer_add(pharmacy, cart)
        elif choice == "4":
            customer_cart(cart)
        elif choice == "5":
            customer_order(pharmacy, cart, state)
        elif choice == "6":
            break
        else:
            print("Invalid choice. Please choose 1-6.")


# --- Main Menu Flow (FR1) ---

def main_menu(pharmacy: Pharmacy):
    """Display main menu for Staff, Customer, and Exit."""
    cart = Cart()
    state = {"order_no": 1001}

    while True:
        print("\n===== MediQuick =====")
        print("1. Staff\n2. Customer\n3. Exit")
        try:
            choice = input("Enter choice: ").strip()
        except (KeyboardInterrupt, EOFError):
            print("\nExiting MediQuick. Goodbye!")
            break

        if choice == "1":
            password = input("Enter staff password: ").strip()
            if password == "admin123":
                staff_menu(pharmacy)
            else:
                print("Incorrect password. Returning to main menu.")
        elif choice == "2":
            customer_menu(pharmacy, cart, state)
        elif choice == "3":
            print("Thank you for using MediQuick. Goodbye!")
            break
        else:
            print("Invalid choice. Please enter 1, 2, or 3.")
