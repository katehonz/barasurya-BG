
from typing import Dict, List, Optional, TypedDict


class InventoryType(TypedDict):
    code: str
    name_bg: str
    name_en: str


class InventoryTypes:
    _types: Dict[str, InventoryType] = {
        "10": {"code": "10", "name_bg": "Материали", "name_en": "Materials"},
        "20": {"code": "20", "name_bg": "Продукция", "name_en": "Finished goods"},
        "30": {"code": "30", "name_bg": "Стоки", "name_en": "Goods for resale"},
        "40": {"code": "40", "name_bg": "Незавършено производство", "name_en": "Work in progress"},
        "50": {"code": "50", "name_bg": "Инвестиция в материален запас", "name_en": "Investment in inventory"},
    }

    @classmethod
    def all_codes(cls) -> List[str]:
        return list(cls._types.keys())

    @classmethod
    def all(cls) -> List[InventoryType]:
        return list(cls._types.values())

    @classmethod
    def get(cls, code: str) -> Optional[InventoryType]:
        return cls._types.get(str(code))

    @classmethod
    def valid(cls, code: str) -> bool:
        return str(code) in cls._types

    @classmethod
    def name_bg(cls, code: str) -> Optional[str]:
        type_ = cls.get(code)
        return type_["name_bg"] if type_ else None

    @classmethod
    def name_en(cls, code: str) -> Optional[str]:
        type_ = cls.get(code)
        return type_["name_en"] if type_ else None

    @classmethod
    def from_product_type(cls, type_: str) -> str:
        mapping = {
            "material": "10",
            "raw_material": "10",
            "finished_good": "20",
            "production": "20",
            "product": "20",
            "goods": "30",
            "merchandise": "30",
            "resale": "30",
            "wip": "40",
            "work_in_progress": "40",
            "investment": "50",
            "service": "30",
        }
        return mapping.get(type_, "30")

