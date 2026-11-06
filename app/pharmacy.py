"""Pharmacy catalogue and CSV persistence."""

import csv
from app.models.medicine import Medicine


class Pharmacy:
    """Manages medicine inventory, file I/O, and search."""

    def __init__(self, filename="medicines.csv"):
        self.filename = filename
        self.medicines = {}
        self.load_from_csv()

    def load_from_csv(self):
        """Load medicines from CSV; handle FileNotFoundError by starting empty."""
        self.medicines.clear()
        try:
            with open(self.filename, mode="r", newline="", encoding="utf-8") as f:
                reader = csv.DictReader(f)
                for row in reader:
                    med = Medicine(
                        code=row["code"],
                        name=row["name"],
                        category=row["category"],
                        price=row["price"],
                        stock=row["stock"],
                        rx=row["rx"],
                    )
                    self.medicines[med.code] = med
        except FileNotFoundError:
            print(f"Warning: '{self.filename}' was not found. Starting with an empty medicine list.")
        except Exception as e:
            print(f"Error reading '{self.filename}': {e}")

    def save_to_csv(self):
        """Save medicines list to CSV file."""
        try:
            with open(self.filename, mode="w", newline="", encoding="utf-8") as f:
                writer = csv.writer(f)
                writer.writerow(["code", "name", "category", "price", "stock", "rx"])
                for m in self.medicines.values():
                    price = int(m.price) if m.price.is_integer() else m.price
                    writer.writerow([m.code, m.name, m.category, price, m.stock, m.rx])
        except Exception as e:
            print(f"Error saving to '{self.filename}': {e}")

    def get_medicine(self, code):
        """Find medicine by code."""
        return self.medicines.get(code.strip().upper())

    def add_medicine(self, medicine):
        """Add medicine to inventory and save."""
        self.medicines[medicine.code] = medicine
        self.save_to_csv()

    def update_medicine(self, code, price=None, stock=None):
        """Update existing medicine price and/or stock and save."""
        med = self.get_medicine(code)
        if med:
            if price is not None:
                med.price = round(float(price), 2)
            if stock is not None:
                med.stock = int(stock)
            self.save_to_csv()
        return med

    def get_all_medicines(self):
        """Return list of all medicines."""
        return list(self.medicines.values())

    def search_by_name(self, query):
        """Case-insensitive substring search by medicine name."""
        q = query.strip().lower()
        return [m for m in self.medicines.values() if q in m.name.lower()]
