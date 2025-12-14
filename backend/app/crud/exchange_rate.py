# Re-export from currency module for backwards compatibility
from app.crud.currency import exchange_rate, CRUDExchangeRate

__all__ = ["exchange_rate", "CRUDExchangeRate"]
