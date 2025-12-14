
from typing import Dict, List, Optional, TypedDict


class PaymentType(TypedDict):
    code: str
    name_bg: str
    name_en: str


class PaymentMethods:
    _methods: Dict[str, PaymentType] = {
        "01": {"code": "01", "name_bg": "Пари в брой", "name_en": "Cash"},
        "02": {"code": "02", "name_bg": "Прихващане", "name_en": "Offset"},
        "03": {"code": "03", "name_bg": "Безкасово плащане", "name_en": "Non-cash payment"},
    }

    _mechanisms: Dict[str, PaymentType] = {
        "10": {"code": "10", "name_bg": "Пари в брой", "name_en": "Cash"},
        "20": {"code": "20", "name_bg": "С чек", "name_en": "By check"},
        "30": {"code": "30", "name_bg": "Ваучер", "name_en": "Voucher"},
        "42": {"code": "42", "name_bg": "Плащане по банкова сметка", "name_en": "Bank transfer"},
        "48": {"code": "48", "name_bg": "Банкова карта", "name_en": "Bank card"},
        "68": {"code": "68", "name_bg": "Услуги за онлайн плащане", "name_en": "Online payment services"},
        "97": {"code": "97", "name_bg": "Прихващане между контрагенти", "name_en": "Offset between counterparties"},
        "98": {"code": "98", "name_bg": "Бартер", "name_en": "Barter"},
        "99": {"code": "99", "name_bg": "Подотчетни лица", "name_en": "Accountable persons"},
    }

    @classmethod
    def all_methods(cls) -> List[PaymentType]:
        return sorted(list(cls._methods.values()), key=lambda x: x["code"])

    @classmethod
    def all_mechanisms(cls) -> List[PaymentType]:
        return sorted(list(cls._mechanisms.values()), key=lambda x: x["code"])

    @classmethod
    def all(cls) -> List[Dict]:
        methods = [{**m, "type": "Метод"} for m in cls.all_methods()]
        mechanisms = [{**m, "type": "Механизъм"} for m in cls.all_mechanisms()]
        return methods + mechanisms

    @classmethod
    def get_method(cls, code: str) -> Optional[PaymentType]:
        return cls._methods.get(str(code))

    @classmethod
    def get_mechanism(cls, code: str) -> Optional[PaymentType]:
        return cls._mechanisms.get(str(code))

    @classmethod
    def valid_method_code(cls, code: str) -> bool:
        return str(code) in cls._methods

    @classmethod
    def valid_mechanism_code(cls, code: str) -> bool:
        return str(code) in cls._mechanisms

    @classmethod
    def method_name_bg(cls, code: str) -> Optional[str]:
        method = cls.get_method(code)
        return method["name_bg"] if method else None

    @classmethod
    def mechanism_name_bg(cls, code: str) -> Optional[str]:
        mechanism = cls.get_mechanism(code)
        return mechanism["name_bg"] if mechanism else None

