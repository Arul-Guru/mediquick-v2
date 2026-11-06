"""MediQuick - Pharmacy Billing System entry point."""

import sys
from app.pharmacy import Pharmacy
from app.ui import main_menu


def main():
    """Start the MediQuick console application."""
    pharmacy = Pharmacy("medicines.csv")
    try:
        main_menu(pharmacy)
    except (KeyboardInterrupt, EOFError):
        print("\nMediQuick session ended.")
        sys.exit(0)


if __name__ == "__main__":
    main()
