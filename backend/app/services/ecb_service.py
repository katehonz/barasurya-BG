import logging
from datetime import date, timedelta
from decimal import Decimal
from typing import Dict, List, Optional, Tuple
from uuid import UUID

import httpx
import xml.etree.ElementTree as ET
from sqlmodel import Session, select

from app.core.config import settings
from app.crud import currency as crud_currency
from app.crud import exchange_rate as crud_exchange_rate
from app.models import Currency, ExchangeRate, ExchangeRateCreate, ExchangeRateUpdate

logger = logging.getLogger(__name__)

# ECB URLs
CURRENT_RATES_URL = "https://www.ecb.europa.eu/stats/eurofxref/eurofxref-daily.xml"
HISTORICAL_RATES_URL = "https://www.ecb.europa.eu/stats/eurofxref/eurofxref-hist.xml"
NINETY_DAY_RATES_URL = (
    "https://www.ecb.europa.eu/stats/eurofxref/eurofxref-hist-90d.xml"
)

# Fixed conversion rate for EUR to BGN (as per EU treaty)
FIXED_EUR_BGN = Decimal("1.95583")

# ECB supported currencies
ECB_SUPPORTED_CURRENCIES = [
    "USD", "JPY", "BGN", "CZK", "DKK", "EEK", "GBP", "HUF", "LTL", "LVL",
    "PLN", "RON", "SEK", "CHF", "NOK", "HRK", "RUB", "TRY", "AUD", "BRL",
    "CAD", "CNY", "HKD", "IDR", "ILS", "INR", "KRW", "MXN", "MYR", "NZD",
    "PHP", "SGD", "THB", "ZAR",
]


async def fetch_xml(url: str, timeout: int = 30) -> httpx.Response:
    """Fetch XML from ECB with proper error handling"""
    try:
        async with httpx.AsyncClient(timeout=timeout) as client:
            response = await client.get(
                url, headers={"User-Agent": "Barasurya-ERP/1.0 (Currency Service)"}
            )
            response.raise_for_status()
            return response
    except httpx.HTTPStatusError as e:
        logger.error(f"HTTP error fetching ECB rates from {url}: {e}")
        raise
    except httpx.RequestError as e:
        logger.error(f"Request error fetching ECB rates: {e}")
        raise
    except Exception as e:
        logger.error(f"Unexpected error fetching ECB rates: {e}")
        raise


def parse_ecb_xml(
    xml_content: str, target_date: Optional[date] = None
) -> Dict[date, Dict[str, Decimal]]:
    """Parse ECB XML and return rates by date"""
    try:
        root = ET.fromstring(xml_content)
        namespaces = {
            "gesmes": "http://www.gesmes.org/xml/2002-08-01",
            "cube": "http://www.ecb.int/vocabulary/2002-08-01/eurofxref",
        }

        rates_by_date = {}
        time_cubes = root.findall(".//cube:Cube[@time]", namespaces)

        for cube in time_cubes:
            time_str = cube.get("time")
            if not time_str:
                continue

            current_date = date.fromisoformat(time_str)

            if target_date and current_date != target_date:
                continue

            daily_rates = {
                rate_cube.get("currency"): Decimal(rate_cube.get("rate"))
                for rate_cube in cube.findall("cube:Cube[@currency]", namespaces)
                if rate_cube.get("currency") and rate_cube.get("rate")
            }

            if daily_rates:
                rates_by_date[current_date] = daily_rates

        return rates_by_date
    except (ET.ParseError, Exception) as e:
        logger.error(f"Error parsing ECB XML: {e}")
        raise


def get_base_currency(db: Session) -> Optional[Currency]:
    """Get base currency from database"""
    return db.exec(select(Currency).where(Currency.is_base_currency)).first()


def get_currency_by_code(db: Session, code: str) -> Optional[Currency]:
    """Get currency by ISO code"""
    return db.exec(select(Currency).where(Currency.code == code.upper())).first()


def is_business_day(d: date) -> bool:
    """Check if date is a business day (Monday-Friday)"""
    return d.weekday() < 5


def get_supported_currencies() -> List[str]:
    """Get list of currencies supported by ECB"""
    return ECB_SUPPORTED_CURRENCIES.copy()


def _calculate_rate_details(
    base_currency: Currency,
    eur_currency: Currency,
    foreign_currency: Currency,
    ecb_rate_value: Decimal,
) -> Tuple[Decimal, UUID, UUID]:
    """Calculate the exchange rate and determine from/to currency IDs."""
    if base_currency.code == "EUR":
        return ecb_rate_value, eur_currency.id, foreign_currency.id

    if base_currency.code == "BGN":
        if foreign_currency.code == "EUR":
            return FIXED_EUR_BGN, eur_currency.id, base_currency.id
        # Convert EUR -> BGN -> Foreign
        bgn_to_foreign = FIXED_EUR_BGN / ecb_rate_value
        return bgn_to_foreign, foreign_currency.id, base_currency.id

    # For other base currencies, use EUR as an intermediary
    return ecb_rate_value, eur_currency.id, foreign_currency.id


def _create_or_update_rate(
    db: Session,
    from_currency_id: UUID,
    to_currency_id: UUID,
    rate: Decimal,
    valid_date: date,
    currency_code: str,
):
    """Create or update an exchange rate in the database."""
    existing_rate = db.exec(
        select(ExchangeRate).where(
            ExchangeRate.from_currency_id == from_currency_id,
            ExchangeRate.to_currency_id == to_currency_id,
            ExchangeRate.valid_date == valid_date,
        )
    ).first()

    try:
        ecb_rate_id = f"ECB_{valid_date}_{currency_code}"
        if existing_rate:
            update_data = ExchangeRateUpdate(
                rate=rate, rate_source="ecb", ecb_rate_id=ecb_rate_id
            )
            crud_exchange_rate.exchange_rate.update(
                db, db_obj=existing_rate, obj_in=update_data
            )
        else:
            create_data = ExchangeRateCreate(
                from_currency_id=from_currency_id,
                to_currency_id=to_currency_id,
                rate=rate,
                valid_date=valid_date,
                rate_source="ecb",
                ecb_rate_id=ecb_rate_id,
            )
            crud_exchange_rate.exchange_rate.create(db, obj_in=create_data)
        return True
    except Exception as e:
        logger.error(f"Failed to create/update rate for {currency_code}: {e}")
        return False


async def _process_date_rates(
    db: Session, target_date: date, daily_rates: Dict[str, Decimal]
) -> int:
    """Process rates for a specific date from pre-fetched data."""
    base_currency = get_base_currency(db)
    eur_currency = get_currency_by_code(db, "EUR")
    if not base_currency or not eur_currency:
        logger.error("Base or EUR currency not found in the database.")
        return 0

    updated_count = 0
    for currency_code, rate_value in daily_rates.items():
        if currency_code not in ECB_SUPPORTED_CURRENCIES:
            continue

        foreign_currency = get_currency_by_code(db, currency_code)
        if not foreign_currency:
            continue

        rate, from_id, to_id = _calculate_rate_details(
            base_currency, eur_currency, foreign_currency, rate_value
        )

        if _create_or_update_rate(
            db, from_id, to_id, rate, target_date, currency_code
        ):
            updated_count += 1

    # Special handling for BGN if base is EUR
    if base_currency.code == "EUR":
        bgn_currency = get_currency_by_code(db, "BGN")
        if bgn_currency and _create_or_update_rate(
            db, eur_currency.id, bgn_currency.id, FIXED_EUR_BGN, target_date, "BGN"
        ):
            updated_count += 1
            
    logger.info(f"Updated {updated_count} exchange rates for {target_date}")
    return updated_count


async def update_rates_for_date(db: Session, target_date: Optional[date] = None) -> int:
    """Update exchange rates for a specific date from ECB."""
    target_date = target_date or date.today()
    days_diff = (date.today() - target_date).days

    if days_diff <= 1:
        url = CURRENT_RATES_URL
    elif days_diff <= 90:
        url = NINETY_DAY_RATES_URL
    else:
        url = HISTORICAL_RATES_URL

    try:
        response = await fetch_xml(url)
        rates_by_date = parse_ecb_xml(response.text, target_date)
        
        if target_date not in rates_by_date:
            logger.warning(f"No rates found for date {target_date}")
            return 0
            
        return await _process_date_rates(db, target_date, rates_by_date[target_date])
        
    except Exception as e:
        logger.error(f"Error fetching or processing ECB rates for {target_date}: {e}")
        return 0


async def update_current_rates(db: Session) -> int:
    """Update current exchange rates, trying today and yesterday."""
    today = date.today()
    if is_business_day(today):
        count = await update_rates_for_date(db, today)
        if count > 0:
            return count

    yesterday = today - timedelta(days=1)
    while not is_business_day(yesterday):
        yesterday -= timedelta(days=1)
        
    return await update_rates_for_date(db, yesterday)


async def update_rates_for_range(
    db: Session, from_date: date, to_date: date
) -> Dict[str, int]:
    """Update exchange rates for a date range."""
    results = {}
    
    days_diff = (to_date - from_date).days
    url = NINETY_DAY_RATES_URL if days_diff <= 90 else HISTORICAL_RATES_URL

    try:
        response = await fetch_xml(url)
        rates_by_date = parse_ecb_xml(response.text)

        current_date = from_date
        while current_date <= to_date:
            if is_business_day(current_date) and current_date in rates_by_date:
                count = await _process_date_rates(
                    db, current_date, rates_by_date[current_date]
                )
                results[current_date.isoformat()] = count
            current_date += timedelta(days=1)
    except Exception as e:
        logger.error(f"Error updating rates for range {from_date}-{to_date}: {e}")

    return results


class ECBRateService:
    """High-level service for ECB rate management"""

    def __init__(self, timeout: int = 30):
        self.timeout = timeout

    async def sync_daily_rates(self, db: Session) -> Dict[str, int]:
        """Sync daily rates from ECB, including recent business days."""
        results = {}
        today = date.today()
        
        # Update rates for today or the last business day
        count = await update_current_rates(db)
        results["current"] = count

        # Optionally, update last few business days
        for i in range(1, 5):
            past_date = today - timedelta(days=i)
            if is_business_day(past_date):
                # Check if rates for this date already exist to avoid refetching
                rate_exists = db.exec(select(ExchangeRate.id).where(ExchangeRate.valid_date == past_date).limit(1)).first()
                if not rate_exists:
                    count = await update_rates_for_date(db, past_date)
                    results[past_date.isoformat()] = count
        return results

    async def sync_historical_rates(
        self, db: Session, days_back: int = 90
    ) -> Dict[str, int]:
        """Sync historical rates for a specified number of days."""
        end_date = date.today()
        start_date = end_date - timedelta(days=days_back)
        return await update_rates_for_range(db, start_date, end_date)

    def get_rate_status(self, db: Session) -> Dict[str, any]:
        """Get status of exchange rates in the database."""
        base_currency = get_base_currency(db)
        latest_rate = db.exec(
            select(ExchangeRate.valid_date)
            .where(ExchangeRate.rate_source == "ecb")
            .order_by(ExchangeRate.valid_date.desc())
            .limit(1)
        ).first()

        total_rates = db.scalar(
            select(func.count(ExchangeRate.id)).where(ExchangeRate.rate_source == "ecb")
        )

        return {
            "base_currency": base_currency.code if base_currency else None,
            "latest_rate_date": latest_rate,
            "total_ecb_rates": total_rates,
            "supported_currencies": get_supported_currencies(),
        }


# Singleton instance
ecb_rate_service = ECBRateService()
