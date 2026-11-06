"""Medicine model representing pharmacy items."""

from app.exceptions.insufficient_stock_error import InsufficientStockError


class Medicine:
    """Holds medicine details and handles stock reduction."""

    def __init__(self, code, name, category, price, stock, rx):
        self.code = str(code).strip().upper()
        self.name = str(name).strip()
        self.category = str(category).strip()
        self.price = round(float(price), 2)
        self.stock = int(stock)
        self.rx = str(rx).strip().upper()

        if self.price <= 0:
            raise ValueError("Price must be greater than zero.")
        if self.stock < 0:
            raise ValueError("Stock cannot be negative.")
        if self.rx not in ("Y", "N"):
            raise ValueError("Rx flag must be 'Y' or 'N'.")

    def reduce_stock(self, quantity):
        """Reduce stock by quantity or raise InsufficientStockError."""
        if quantity <= 0:
            raise ValueError("Quantity must be positive.")
        if quantity > self.stock:
            raise InsufficientStockError(f"Insufficient stock for {self.name}.")
        self.stock -= quantity

    def is_out_of_stock(self):
        """Check if stock is zero."""
        return self.stock <= 0
