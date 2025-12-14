
from typing import Dict, List, Optional, TypedDict


class AssetMovementType(TypedDict):
    code: str
    short: str
    name_bg: str
    name_en: str


class AssetMovementTypes:
    _types: Dict[str, AssetMovementType] = {
        "10": {"code": "10", "short": "ACQ", "name_bg": "Придобиване", "name_en": "Acquisition"},
        "20": {"code": "20", "short": "IMP", "name_bg": "Подобрение/Увеличаване", "name_en": "Improvement"},
        "30": {"code": "30", "short": "DEP", "name_bg": "Амортизация", "name_en": "Depreciation"},
        "40": {"code": "40", "short": "REV", "name_bg": "Преоценка", "name_en": "Revaluation"},
        "50": {"code": "50", "short": "DSP", "name_bg": "Продажба", "name_en": "Disposal/Sale"},
        "60": {"code": "60", "short": "SCR", "name_bg": "Брак/Отписване", "name_en": "Scrap/Write-off"},
        "70": {"code": "70", "short": "TRF", "name_bg": "Вътрешен трансфер", "name_en": "Internal transfer"},
        "80": {"code": "80", "short": "COR", "name_bg": "Корекция", "name_en": "Correction"},
    }

    @classmethod
    def all_codes(cls) -> List[str]:
        return list(cls._types.keys())

    @classmethod
    def all(cls) -> List[AssetMovementType]:
        return list(cls._types.values())

    @classmethod
    def get(cls, code: str) -> Optional[AssetMovementType]:
        return cls._types.get(str(code))

    @classmethod
    def valid(cls, code: str) -> bool:
        return str(code) in cls._types

    @classmethod
    def name_bg(cls, code: str) -> Optional[str]:
        type_ = cls.get(code)
        return type_["name_bg"] if type_ else None

    @classmethod
    def short_name(cls, code: str) -> Optional[str]:
        type_ = cls.get(code)
        return type_["short"] if type_ else None

    @classmethod
    def full_description(cls, code: str) -> Optional[str]:
        type_ = cls.get(code)
        if not type_:
            return None
        return f"{type_['code']}: {type_['short']} - {type_['name_bg']}"

    @classmethod
    def from_internal_type(cls, type_: str) -> str:
        mapping = {
            "acquisition": "10",
            "purchase": "10",
            "improvement": "20",
            "increase": "20",
            "depreciation": "30",
            "revaluation": "40",
            "sale": "50",
            "disposal": "50",
            "scrap": "60",
            "write_off": "60",
            "transfer": "70",
            "correction": "80",
        }
        return mapping.get(type_, "80")

