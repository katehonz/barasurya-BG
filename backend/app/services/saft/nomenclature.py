# TODO: Implement SAFT nomenclature types
from enum import Enum


class AssetMovementType(str, Enum):
    ACQUISITION = "acquisition"
    DEPRECIATION = "depreciation"
    DISPOSAL = "disposal"
    REVALUATION = "revaluation"


class StockMovementType(str, Enum):
    PURCHASE = "purchase"
    SALE = "sale"
    ADJUSTMENT = "adjustment"
    TRANSFER = "transfer"
