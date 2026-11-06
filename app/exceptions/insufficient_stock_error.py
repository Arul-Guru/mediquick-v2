"""Custom exception for stock insufficiency."""


class InsufficientStockError(Exception):
    """Raised when requested quantity exceeds available stock."""

    pass
