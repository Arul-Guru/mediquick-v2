"""Tests strictly for deterministic calculation scenarios in MediQuick."""

import pytest
from app.exceptions.insufficient_stock_error import InsufficientStockError
from app.models.cart import Cart
from app.models.medicine import Medicine


def test_line_total_calculation():
    """Verify calculation of line total for a single medicine item."""
    med = Medicine(
        code="T01",
        name="Paracetamol 500mg",
        category="Tablets",
        price=25.0,
        stock=50,
        rx="N",
    )
    cart = Cart()
    cart.add(med, 2)
    # 2 * 25.00 = 50.00
    assert cart.calculate_subtotal() == 50.00


def test_multiple_items_subtotal_calculation():
    """Verify subtotal calculation across multiple distinct cart items."""
    med1 = Medicine(
        code="T01",
        name="Paracetamol 500mg",
        category="Tablets",
        price=25.0,
        stock=50,
        rx="N",
    )
    med2 = Medicine(
        code="S01",
        name="Cough Syrup 100ml",
        category="Syrups",
        price=70.0,
        stock=20,
        rx="N",
    )
    cart = Cart()
    cart.add(med1, 2)  # 50.00
    cart.add(med2, 1)  # 70.00

    # 50.00 + 70.00 = 120.00
    assert cart.calculate_subtotal() == 120.00


def test_gst_twelve_percent_calculation():
    """Verify flat 12% GST calculation on subtotal."""
    cart = Cart()
    # 12% of 120.00 = 14.40
    gst = cart.calculate_gst(subtotal=120.00)
    assert gst == 14.40


def test_grand_total_calculation():
    """Verify grand total is accurately the sum of subtotal and GST."""
    cart = Cart()
    subtotal = 120.00
    gst = 14.40
    grand_total = cart.calculate_grand_total(subtotal=subtotal, gst=gst)
    # 120.00 + 14.40 = 134.40
    assert grand_total == 134.40


def test_totals_tuple_calculation():
    """Verify calculate_totals returns correct (subtotal, gst, grand_total) tuple."""
    med1 = Medicine(
        code="T01",
        name="Paracetamol 500mg",
        category="Tablets",
        price=25.0,
        stock=50,
        rx="N",
    )
    med2 = Medicine(
        code="S01",
        name="Cough Syrup 100ml",
        category="Syrups",
        price=70.0,
        stock=20,
        rx="N",
    )
    cart = Cart()
    cart.add(med1, 2)
    cart.add(med2, 1)

    subtotal, gst, grand_total = cart.calculate_totals()
    assert subtotal == 120.00
    assert gst == 14.40
    assert grand_total == 134.40


def test_decimal_rounding_calculations():
    """Verify rounding to 2 decimal places for non-integer pricing calculations."""
    med = Medicine(
        code="W02",
        name="Electrolyte Sachet",
        category="Wellness",
        price=19.99,
        stock=10,
        rx="N",
    )
    cart = Cart()
    cart.add(med, 3)

    # 3 * 19.99 = 59.97
    subtotal = cart.calculate_subtotal()
    assert subtotal == 59.97

    # 59.97 * 0.12 = 7.1964 -> rounds to 7.20
    gst = cart.calculate_gst(subtotal)
    assert gst == 7.20

    # 59.97 + 7.20 = 67.17
    grand_total = cart.calculate_grand_total(subtotal, gst)
    assert grand_total == 67.17


def test_repeated_item_addition_quantity_and_subtotal():
    """Verify adding the same item repeatedly increases quantity and updates subtotal."""
    med = Medicine(
        code="T01",
        name="Paracetamol 500mg",
        category="Tablets",
        price=25.0,
        stock=50,
        rx="N",
    )
    cart = Cart()
    cart.add(med, 2)
    assert cart.calculate_subtotal() == 50.00
    assert cart.items["T01"]["quantity"] == 2

    cart.add(med, 3)
    assert cart.calculate_subtotal() == 125.00
    assert cart.items["T01"]["quantity"] == 5


def test_cart_item_removal_subtotal_update():
    """Verify removing an item from the cart recalculates subtotal and totals."""
    med1 = Medicine(
        code="T01",
        name="Paracetamol 500mg",
        category="Tablets",
        price=25.0,
        stock=50,
        rx="N",
    )
    med2 = Medicine(
        code="S01",
        name="Cough Syrup 100ml",
        category="Syrups",
        price=70.0,
        stock=20,
        rx="N",
    )
    cart = Cart()
    cart.add(med1, 2)  # 50.00
    cart.add(med2, 1)  # 70.00
    assert cart.calculate_subtotal() == 120.00

    removed = cart.remove("T01")
    assert removed is True
    assert cart.calculate_subtotal() == 70.00
    assert cart.calculate_gst() == 8.40
    assert cart.calculate_grand_total() == 78.40


def test_stock_reduction_calculation():
    """Verify stock reduction decreases available stock deterministically."""
    med = Medicine(
        code="T01",
        name="Paracetamol 500mg",
        category="Tablets",
        price=25.0,
        stock=60,
        rx="N",
    )
    initial_stock = med.stock
    order_quantity = 5
    med.reduce_stock(order_quantity)
    assert med.stock == initial_stock - order_quantity
    assert med.stock == 55


def test_insufficient_stock_error_on_exceeded_quantity():
    """Verify InsufficientStockError is raised when requested quantity exceeds stock."""
    med = Medicine(
        code="T02",
        name="Amoxicillin 250mg",
        category="Tablets",
        price=85.0,
        stock=8,
        rx="Y",
    )
    cart = Cart()
    with pytest.raises(InsufficientStockError):
        cart.add(med, 10)

    # Medicine direct reduction should also raise InsufficientStockError
    with pytest.raises(InsufficientStockError):
        med.reduce_stock(9)
