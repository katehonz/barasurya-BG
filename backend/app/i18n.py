"""
Интернационализация (i18n) модул за ERP системата.
Поддържа български и английски език.
"""
import gettext
from pathlib import Path
from typing import Callable

LOCALES_DIR = Path(__file__).parent / "locales"
SUPPORTED_LANGUAGES = ["bg", "en"]
DEFAULT_LANGUAGE = "bg"

_translations: dict[str, gettext.GNUTranslations | gettext.NullTranslations] = {}


def get_translation(lang: str) -> gettext.GNUTranslations | gettext.NullTranslations:
    """Връща превод за даден език."""
    if lang not in SUPPORTED_LANGUAGES:
        lang = DEFAULT_LANGUAGE

    if lang not in _translations:
        try:
            _translations[lang] = gettext.translation(
                "messages",
                localedir=str(LOCALES_DIR),
                languages=[lang],
            )
        except FileNotFoundError:
            _translations[lang] = gettext.NullTranslations()

    return _translations[lang]


def gettext_func(lang: str) -> Callable[[str], str]:
    """Връща функция за превод за даден език."""
    translation = get_translation(lang)
    return translation.gettext


def _(message: str, lang: str = DEFAULT_LANGUAGE) -> str:
    """Превежда съобщение на зададения език."""
    return gettext_func(lang)(message)


# Преводи по подразбиране (български)
TRANSLATIONS_BG = {
    # Общи
    "Welcome": "Добре дошли",
    "Login": "Вход",
    "Logout": "Изход",
    "Register": "Регистрация",
    "Email": "Имейл",
    "Password": "Парола",
    "Confirm Password": "Потвърди парола",
    "Submit": "Изпрати",
    "Cancel": "Отказ",
    "Save": "Запази",
    "Delete": "Изтрий",
    "Edit": "Редактирай",
    "Create": "Създай",
    "Search": "Търси",
    "Filter": "Филтрирай",
    "Export": "Експорт",
    "Import": "Импорт",
    "Settings": "Настройки",
    "Profile": "Профил",
    "Dashboard": "Табло",
    "Home": "Начало",

    # Потребители
    "Users": "Потребители",
    "User": "Потребител",
    "Full Name": "Пълно име",
    "Username": "Потребителско име",
    "Role": "Роля",
    "Admin": "Администратор",
    "Active": "Активен",
    "Inactive": "Неактивен",

    # Съобщения за грешки
    "Invalid credentials": "Невалидни данни за вход",
    "User not found": "Потребителят не е намерен",
    "Email already registered": "Имейлът вече е регистриран",
    "Password too short": "Паролата е твърде кратка",
    "Passwords do not match": "Паролите не съвпадат",
    "Invalid email": "Невалиден имейл",
    "Unauthorized": "Неоторизиран достъп",
    "Forbidden": "Забранен достъп",
    "Not found": "Не е намерено",
    "Internal server error": "Вътрешна грешка на сървъра",

    # ERP модули
    "Products": "Продукти",
    "Product": "Продукт",
    "Customers": "Клиенти",
    "Customer": "Клиент",
    "Suppliers": "Доставчици",
    "Supplier": "Доставчик",
    "Orders": "Поръчки",
    "Order": "Поръчка",
    "Invoices": "Фактури",
    "Invoice": "Фактура",
    "Inventory": "Склад",
    "Stock": "Наличност",
    "Reports": "Отчети",
    "Report": "Отчет",
    "Accounting": "Счетоводство",
    "Sales": "Продажби",
    "Purchases": "Покупки",
    "Payments": "Плащания",
    "Payment": "Плащане",

    # Полета
    "Name": "Име",
    "Description": "Описание",
    "Price": "Цена",
    "Quantity": "Количество",
    "Total": "Общо",
    "Subtotal": "Междинна сума",
    "Tax": "ДДС",
    "Discount": "Отстъпка",
    "Date": "Дата",
    "Created at": "Създадено на",
    "Updated at": "Обновено на",
    "Status": "Статус",
    "Notes": "Бележки",
    "Address": "Адрес",
    "Phone": "Телефон",
    "Company": "Фирма",
    "VAT Number": "ЕИК/Булстат",
    "City": "Град",
    "Country": "Държава",
    "Postal Code": "Пощенски код",

    # Статуси
    "Pending": "Изчакващ",
    "Approved": "Одобрен",
    "Rejected": "Отхвърлен",
    "Completed": "Завършен",
    "Cancelled": "Отменен",
    "In Progress": "В процес",
    "Draft": "Чернова",
    "Paid": "Платено",
    "Unpaid": "Неплатено",
    "Overdue": "Просрочено",
}


def translate_bg(message: str) -> str:
    """Бърз превод на български."""
    return TRANSLATIONS_BG.get(message, message)
