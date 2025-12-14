
from typing import Dict, List, Optional, TypedDict


class VatTaxType(TypedDict):
    code: str
    name_bg: str
    name_en: str


class VatTaxTypes:
    _types: Dict[str, VatTaxType] = {
        "100010": {
            "code": "100010",
            "name_bg": "Данъчно задължено лице, регистрирано за целите на ДДС",
            "name_en": "VAT registered taxable person",
        },
        "100020": {
            "code": "100020",
            "name_bg": "Всяко друго данъчно задължено лице",
            "name_en": "Other taxable person",
        },
        "100030": {
            "code": "100030",
            "name_bg": "Данъчно незадължено лице",
            "name_en": "Non-taxable person",
        },
    }

    @classmethod
    def all_codes(cls) -> List[str]:
        return list(cls._types.keys())

    @classmethod
    def all(cls) -> List[VatTaxType]:
        return list(cls._types.values())

    @classmethod
    def get(cls, code: str) -> Optional[VatTaxType]:
        return cls._types.get(str(code))

    @classmethod
    def valid(cls, code: str) -> bool:
        return str(code) in cls._types

    @classmethod
    def name_bg(cls, code: str) -> Optional[str]:
        type_ = cls.get(code)
        return type_["name_bg"] if type_ else None

    @classmethod
    def from_vat_status(cls, is_vat_registered: bool, is_taxable: bool = True) -> str:
        if is_vat_registered:
            return "100010"
        if is_taxable:
            return "100020"
        return "100030"

