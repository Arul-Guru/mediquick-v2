"""Cart model managing customer chosen items and totals."""

from app.exceptions.insufficient_stock_error import InsufficientStockError


class Cart:
    """Manages chosen items, quantities, and bill calculations."""

    def __init__(self):
        self.items = {}  # code: {"medicine": Medicine, "quantity": int}

    def add(self, medicine, quantity):
        """Add medicine to cart or increase quantity if already present."""
        if quantity <= 0:
            raise ValueError("Quantity must be positive.")
        code = medicine.code
        in_cart = self.items.get(code, {}).get("quantity", 0)
        if in_cart + quantity > medicine.stock:
            raise InsufficientStockError("Requested quantity exceeds available stock.")
        if code in self.items:
            self.items[code]["quantity"] += quantity
        else:
            self.items[code] = {"medicine": medicine, "quantity": quantity}

    def remove(self, code):
        """Remove an item line from cart by item code."""
        return self.items.pop(code.strip().upper(), None) is not None

    def calculate_subtotal(self):
        """Calculate total sum of items in cart."""
        return round(sum(i["medicine"].price * i["quantity"] for i in self.items.values()), 2)

    def calculate_gst(self, subtotal=None):
        """Calculate flat 12% GST on subtotal."""
        sub = self.calculate_subtotal() if subtotal is None else subtotal
        return round(sub * 0.12, 2)

    def calculate_grand_total(self, subtotal=None, gst=None):
        """Calculate grand total including subtotal and GST."""
        sub = self.calculate_subtotal() if subtotal is None else subtotal
        tax = self.calculate_gst(sub) if gst is None else gst
        return round(sub + tax, 2)

    def calculate_totals(self):
        """Return tuple of (subtotal, gst, grand_total)."""
        sub = self.calculate_subtotal()
        gst = self.calculate_gst(sub)
        return sub, gst, round(sub + gst, 2)

    def is_empty(self):
        """Check if cart has no items."""
        return len(self.items) == 0

    def clear(self):
        """Empty the cart."""
        self.items.clear()
