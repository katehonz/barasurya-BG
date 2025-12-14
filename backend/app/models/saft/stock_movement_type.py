
from typing import Dict, List, Optional, TypedDict


class StockMovementType(TypedDict):
    code: str
    name_bg: str
    name_en: str


class StockMovementTypes:
    _types: Dict[str, StockMovementType] = {
        "10": {"code": "10", "name_bg": "Покупка", "name_en": "Purchase"},
        "20": {"code": "20", "name_bg": "Материални запаси от производство /продукция/", "name_en": "Production output"},
        "30": {"code": "30", "name_bg": "Продажба", "name_en": "Sale"},
        "40": {"code": "40", "name_bg": "Връщане на продадени продукти", "name_en": "Return of sold products"},
        "50": {"code": "50", "name_bg": "Връщане на закупени продукти", "name_en": "Return of purchased products"},
        "60": {"code": "60", "name_bg": "Получени отстъпки в натура", "name_en": "Discounts received in kind"},
        "65": {"code": "65", "name_bg": "Предоставени отстъпки в натура", "name_en": "Discounts given in kind"},
        "70": {"code": "70", "name_bg": "Материални запаси за производство", "name_en": "Inventory for production"},
        "80": {"code": "80", "name_bg": "Вътрешен трансфер", "name_en": "Internal transfer"},
        "90": {"code": "90", "name_bg": "Последващи разходи, капитализирани в стойността на стоките", "name_en": "Subsequent costs capitalized"},
        "100": {"code": "100", "name_bg": "Положителна ценова разлика", "name_en": "Positive price difference"},
        "101": {"code": "101", "name_bg": "Отрицателна ценова разлика", "name_en": "Negative price difference"},
        "110": {"code": "110", "name_bg": "Положителна корекция от инвентаризацията", "name_en": "Positive inventory adjustment"},
        "120": {"code": "120", "name_bg": "Отрицателна корекция от инвентаризацията", "name_en": "Negative inventory adjustment"},
        "130": {"code": "130", "name_bg": "Увеличение от преоценка на материалните запаси", "name_en": "Revaluation increase"},
        "140": {"code": "140", "name_bg": "Намаление от преоценка на материалните запаси", "name_en": "Revaluation decrease"},
        "150": {"code": "150", "name_bg": "Безвъзмездно предоставени материални запаси", "name_en": "Donated inventory"},
        "160": {"code": "160", "name_bg": "Брак на материални запаси", "name_en": "Scrapped inventory"},
        "170": {"code": "170", "name_bg": "Материални запаси с изтекъл срок на годност", "name_en": "Expired inventory"},
        "180": {"code": "180", "name_bg": "Други движения на материални запаси", "name_en": "Other inventory movements"},
    }

    @classmethod
    def all_codes(cls) -> List[str]:
        return list(cls._types.keys())

    @classmethod
    def all(cls) -> List[StockMovementType]:
        return list(cls._types.values())

    @classmethod
    def get(cls, code: str) -> Optional[StockMovementType]:
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
    def from_internal_type(cls, type_: str) -> str:
        mapping = {
            "purchase": "10",
            "production_output": "20",
            "sale": "30",
            "sales_return": "40",
            "purchase_return": "50",
            "discount_received": "60",
            "discount_given": "65",
            "production_input": "70",
            "transfer": "80",
            "capitalized_costs": "90",
            "price_increase": "100",
            "price_decrease": "101",
            "inventory_surplus": "110",
            "inventory_shortage": "120",
            "revaluation_increase": "130",
            "revaluation_decrease": "140",
            "donation": "150",
            "scrap": "160",
            "expired": "170",
            "other": "180",
        }
        return mapping.get(type_, "180")

