from sqlmodel import Session, create_engine, select

from app import crud
from app.core.config import settings
from app.models import User, UserCreate, Currency, CurrencyCreate
from app.crud import currency as crud_currency

engine = create_engine(str(settings.SQLALCHEMY_DATABASE_URI))


# make sure all SQLModel models are imported (app.models) before initializing DB
# otherwise, SQLModel might fail to initialize relationships properly
# for more details: https://github.com/fastapi/full-stack-fastapi-template/issues/28


def init_db(session: Session) -> None:
    # Tables should be created with Alembic migrations
    # But if you don't want to use migrations, create
    # the tables un-commenting the next lines
    # from sqlmodel import SQLModel

    # This works because the models are already imported and registered from app.models
    # SQLModel.metadata.create_all(engine)

    user = session.exec(
        select(User).where(User.email == settings.FIRST_SUPERUSER)
    ).first()
    if not user:
        user_in = UserCreate(
            email=settings.FIRST_SUPERUSER,
            password=settings.FIRST_SUPERUSER_PASSWORD,
            is_superuser=True,
        )
        user = crud.create_user(session=session, user_create=user_in)


def create_initial_currencies(session: Session) -> None:
    """Create initial currencies with ECB support"""
    currencies_data = [
        {
            "code": "BGN",
            "name": "Bulgarian Lev",
            "name_bg": "Български лев",
            "symbol": "лв",
            "decimal_places": 2,
            "is_active": True,
            "is_base_currency": True,
            "bnb_code": "BGN",
            "ecb_code": "BGN",
        },
        {
            "code": "EUR",
            "name": "Euro",
            "name_bg": "Евро",
            "symbol": "€",
            "decimal_places": 2,
            "is_active": True,
            "is_base_currency": False,
            "bnb_code": "978",
            "ecb_code": "EUR",
        },
        {
            "code": "USD",
            "name": "US Dollar",
            "name_bg": "Американски долар",
            "symbol": "$",
            "decimal_places": 2,
            "is_active": True,
            "is_base_currency": False,
            "bnb_code": "840",
            "ecb_code": "USD",
        },
        {
            "code": "GBP",
            "name": "British Pound",
            "name_bg": "Британска паунд",
            "symbol": "£",
            "decimal_places": 2,
            "is_active": True,
            "is_base_currency": False,
            "bnb_code": "826",
            "ecb_code": "GBP",
        },
        {
            "code": "CHF",
            "name": "Swiss Franc",
            "name_bg": "Швейцарски франк",
            "symbol": "Fr",
            "decimal_places": 2,
            "is_active": True,
            "is_base_currency": False,
            "bnb_code": "756",
            "ecb_code": "CHF",
        },
        {
            "code": "JPY",
            "name": "Japanese Yen",
            "name_bg": "Японска йена",
            "symbol": "¥",
            "decimal_places": 0,
            "is_active": True,
            "is_base_currency": False,
            "bnb_code": "392",
            "ecb_code": "JPY",
        },
        {
            "code": "CZK",
            "name": "Czech Koruna",
            "name_bg": "Чешка крона",
            "symbol": "Kč",
            "decimal_places": 2,
            "is_active": True,
            "is_base_currency": False,
            "bnb_code": "203",
            "ecb_code": "CZK",
        },
        {
            "code": "DKK",
            "name": "Danish Krone",
            "name_bg": "Датска крона",
            "symbol": "kr",
            "decimal_places": 2,
            "is_active": True,
            "is_base_currency": False,
            "bnb_code": "208",
            "ecb_code": "DKK",
        },
        {
            "code": "HUF",
            "name": "Hungarian Forint",
            "name_bg": "Унгарски форинт",
            "symbol": "Ft",
            "decimal_places": 2,
            "is_active": True,
            "is_base_currency": False,
            "bnb_code": "348",
            "ecb_code": "HUF",
        },
        {
            "code": "PLN",
            "name": "Polish Zloty",
            "name_bg": "Полска злота",
            "symbol": "zł",
            "decimal_places": 2,
            "is_active": True,
            "is_base_currency": False,
            "bnb_code": "985",
            "ecb_code": "PLN",
        },
        {
            "code": "RON",
            "name": "Romanian Leu",
            "name_bg": "Румънска лея",
            "symbol": "lei",
            "decimal_places": 2,
            "is_active": True,
            "is_base_currency": False,
            "bnb_code": "946",
            "ecb_code": "RON",
        },
        {
            "code": "SEK",
            "name": "Swedish Krona",
            "name_bg": "Шведска крона",
            "symbol": "kr",
            "decimal_places": 2,
            "is_active": True,
            "is_base_currency": False,
            "bnb_code": "752",
            "ecb_code": "SEK",
        },
        {
            "code": "NOK",
            "name": "Norwegian Krone",
            "name_bg": "Норвежка крона",
            "symbol": "kr",
            "decimal_places": 2,
            "is_active": True,
            "is_base_currency": False,
            "bnb_code": "578",
            "ecb_code": "NOK",
        },
        {
            "code": "HRK",
            "name": "Croatian Kuna",
            "name_bg": "Хърватска куна",
            "symbol": "kn",
            "decimal_places": 2,
            "is_active": True,
            "is_base_currency": False,
            "bnb_code": "191",
            "ecb_code": "HRK",
        },
        {
            "code": "RUB",
            "name": "Russian Ruble",
            "name_bg": "Руска рубла",
            "symbol": "₽",
            "decimal_places": 2,
            "is_active": True,
            "is_base_currency": False,
            "bnb_code": "643",
            "ecb_code": "RUB",
        },
        {
            "code": "TRY",
            "name": "Turkish Lira",
            "name_bg": "Турска лира",
            "symbol": "₺",
            "decimal_places": 2,
            "is_active": True,
            "is_base_currency": False,
            "bnb_code": "949",
            "ecb_code": "TRY",
        },
        {
            "code": "AUD",
            "name": "Australian Dollar",
            "name_bg": "Австралийски долар",
            "symbol": "A$",
            "decimal_places": 2,
            "is_active": True,
            "is_base_currency": False,
            "bnb_code": "036",
            "ecb_code": "AUD",
        },
        {
            "code": "BRL",
            "name": "Brazilian Real",
            "name_bg": "Бразилски реал",
            "symbol": "R$",
            "decimal_places": 2,
            "is_active": True,
            "is_base_currency": False,
            "bnb_code": "986",
            "ecb_code": "BRL",
        },
        {
            "code": "CAD",
            "name": "Canadian Dollar",
            "name_bg": "Канадски долар",
            "symbol": "C$",
            "decimal_places": 2,
            "is_active": True,
            "is_base_currency": False,
            "bnb_code": "124",
            "ecb_code": "CAD",
        },
        {
            "code": "CNY",
            "name": "Chinese Yuan",
            "name_bg": "Китайски юан",
            "symbol": "¥",
            "decimal_places": 2,
            "is_active": True,
            "is_base_currency": False,
            "bnb_code": "156",
            "ecb_code": "CNY",
        },
        {
            "code": "HKD",
            "name": "Hong Kong Dollar",
            "name_bg": "Хонконгски долар",
            "symbol": "HK$",
            "decimal_places": 2,
            "is_active": True,
            "is_base_currency": False,
            "bnb_code": "344",
            "ecb_code": "HKD",
        },
        {
            "code": "IDR",
            "name": "Indonesian Rupiah",
            "name_bg": "Индонезийска рупия",
            "symbol": "Rp",
            "decimal_places": 0,
            "is_active": True,
            "is_base_currency": False,
            "bnb_code": "360",
            "ecb_code": "IDR",
        },
        {
            "code": "ILS",
            "name": "Israeli Shekel",
            "name_bg": "Израелски шекел",
            "symbol": "₪",
            "decimal_places": 2,
            "is_active": True,
            "is_base_currency": False,
            "bnb_code": "376",
            "ecb_code": "ILS",
        },
        {
            "code": "INR",
            "name": "Indian Rupee",
            "name_bg": "Индийска рупия",
            "symbol": "₹",
            "decimal_places": 2,
            "is_active": True,
            "is_base_currency": False,
            "bnb_code": "356",
            "ecb_code": "INR",
        },
        {
            "code": "KRW",
            "name": "Korean Won",
            "name_bg": "Корейски вон",
            "symbol": "₩",
            "decimal_places": 0,
            "is_active": True,
            "is_base_currency": False,
            "bnb_code": "410",
            "ecb_code": "KRW",
        },
        {
            "code": "MXN",
            "name": "Mexican Peso",
            "name_bg": "Мексиканско песо",
            "symbol": "$",
            "decimal_places": 2,
            "is_active": True,
            "is_base_currency": False,
            "bnb_code": "484",
            "ecb_code": "MXN",
        },
        {
            "code": "MYR",
            "name": "Malaysian Ringgit",
            "name_bg": "Малайзийски рингит",
            "symbol": "RM",
            "decimal_places": 2,
            "is_active": True,
            "is_base_currency": False,
            "bnb_code": "458",
            "ecb_code": "MYR",
        },
        {
            "code": "NZD",
            "name": "New Zealand Dollar",
            "name_bg": "Новозеландски долар",
            "symbol": "NZ$",
            "decimal_places": 2,
            "is_active": True,
            "is_base_currency": False,
            "bnb_code": "554",
            "ecb_code": "NZD",
        },
        {
            "code": "PHP",
            "name": "Philippine Peso",
            "name_bg": "Филипинско песо",
            "symbol": "₱",
            "decimal_places": 2,
            "is_active": True,
            "is_base_currency": False,
            "bnb_code": "608",
            "ecb_code": "PHP",
        },
        {
            "code": "SGD",
            "name": "Singapore Dollar",
            "name_bg": "Сингапурски долар",
            "symbol": "S$",
            "decimal_places": 2,
            "is_active": True,
            "is_base_currency": False,
            "bnb_code": "702",
            "ecb_code": "SGD",
        },
        {
            "code": "THB",
            "name": "Thai Baht",
            "name_bg": "Тайландски бат",
            "symbol": "฿",
            "decimal_places": 2,
            "is_active": True,
            "is_base_currency": False,
            "bnb_code": "764",
            "ecb_code": "THB",
        },
        {
            "code": "ZAR",
            "name": "South African Rand",
            "name_bg": "Южноафрикански ранд",
            "symbol": "R",
            "decimal_places": 2,
            "is_active": True,
            "is_base_currency": False,
            "bnb_code": "710",
            "ecb_code": "ZAR",
        },
    ]

    for currency_data in currencies_data:
        existing_currency = session.exec(
            select(Currency).where(Currency.code == currency_data["code"])
        ).first()

        if not existing_currency:
            currency_in = CurrencyCreate(**currency_data)
            crud_currency.create(session=session, obj_in=currency_in)

    # Create initial currencies
    create_initial_currencies(session)
