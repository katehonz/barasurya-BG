import logging
from datetime import date, timedelta
from decimal import Decimal
from typing import Dict, List, Optional

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
    "USD",
    "JPY",
    "BGN",
    "CZK",
    "DKK",
    "EEK",
    "GBP",
    "HUF",
    "LTL",
    "LVL",
    "PLN",
    "RON",
    "SEK",
    "CHF",
    "NOK",
    "HRK",
    "RUB",
    "TRY",
    "AUD",
    "BRL",
    "CAD",
    "CNY",
    "HKD",
    "IDR",
    "ILS",
    "INR",
    "KRW",
    "MXN",
    "MYR",
    "NZD",
    "PHP",
    "SGD",
    "THB",
    "ZAR",
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
    xml_content: str, target_date: date = None
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

            # If target_date specified, only process that date
            if target_date and current_date != target_date:
                continue

            daily_rates = {}
            for rate_cube in cube.findall("cube:Cube[@currency]", namespaces):
                currency_code = rate_cube.get("currency")
                rate_str = rate_cube.get("rate")

                if currency_code and rate_str:
                    daily_rates[currency_code] = Decimal(rate_str)

            if daily_rates:
                rates_by_date[current_date] = daily_rates

        return rates_by_date

    except ET.ParseError as e:
        logger.error(f"Error parsing ECB XML: {e}")
        raise
    except Exception as e:
        logger.error(f"Unexpected error parsing ECB XML: {e}")
        raise


def get_base_currency(db: Session) -> Optional[Currency]:
    """Get base currency from database"""
    return db.exec(select(Currency).where(Currency.is_base_currency == True)).first()


def get_currency_by_code(db: Session, code: str) -> Optional[Currency]:
    """Get currency by ISO code"""
    return db.exec(select(Currency).where(Currency.code == code.upper())).first()


def is_business_day(d: date) -> bool:
    """Check if date is a business day (Monday-Friday)"""
    return 1 <= d.weekday() <= 5


def is_currency_supported(currency_code: str) -> bool:
    """Check if currency is supported by ECB"""
    return currency_code.upper() in ECB_SUPPORTED_CURRENCIES


def get_supported_currencies() -> List[str]:
    """Get list of currencies supported by ECB"""
    return ECB_SUPPORTED_CURRENCIES.copy()


async def update_rates_for_date(db: Session, target_date: date = None) -> int:
    """Update exchange rates for a specific date from ECB"""
    if target_date is None:
        target_date = date.today()

    today = date.today()
    days_diff = (today - target_date).days

    # Choose appropriate URL based on date range
    if days_diff <= 1:
        url = CURRENT_RATES_URL
    elif days_diff <= 90:
        url = NINETY_DAY_RATES_URL
    else:
        url = HISTORICAL_RATES_URL

    try:
        response = await fetch_xml(url)
    except Exception as e:
        logger.error(f"Error fetching ECB rates: {e}")
        return 0

    rates_by_date = parse_ecb_xml(response.text, target_date)
    if target_date not in rates_by_date:
        logger.warning(f"No rates found for date {target_date}")
        return 0

    ecb_rates = rates_by_date[target_date]
    base_currency = get_base_currency(db)
    if not base_currency:
        logger.error("No base currency found in database")
        return 0

    is_eur_base = base_currency.code == "EUR"
    eur_currency = get_currency_by_code(db, "EUR")
    if not eur_currency:
        logger.error("EUR currency not found in database")
        return 0

    updated_count = 0
    for currency_code, rate_value in ecb_rates.items():
        # Skip if currency not supported
        if not is_currency_supported(currency_code):
            logger.debug(f"Currency {currency_code} not supported by ECB, skipping")
            continue

        foreign_currency = get_currency_by_code(db, currency_code)
        if not foreign_currency:
            logger.debug(f"Currency {currency_code} not found in database, skipping")
            continue

        # Calculate rate based on base currency
        if is_eur_base:
            # EUR is base, EUR -> foreign
            rate = rate_value
            from_id = eur_currency.id
            to_id = foreign_currency.id
        else:
            # BGN is base, need to convert EUR -> BGN -> foreign
            if base_currency.code == "BGN":
                # EUR -> BGN (fixed), then BGN -> foreign
                bgn_to_foreign = FIXED_EUR_BGN / rate_value
                rate = bgn_to_foreign
                from_id = foreign_currency.id  # foreign -> BGN
                to_id = base_currency.id
            else:
                # For other base currencies, use EUR as intermediary
                rate = rate_value
                from_id = eur_currency.id
                to_id = foreign_currency.id

        # Check if rate already exists
        existing_rate = db.exec(
            select(ExchangeRate).where(
                ExchangeRate.from_currency_id == from_id,
                ExchangeRate.to_currency_id == to_id,
                ExchangeRate.valid_date == target_date,
            )
        ).first()

        try:
            if existing_rate:
                update_data = ExchangeRateUpdate(
                    rate=rate,
                    rate_source="ecb",
                    ecb_rate_id=f"ECB_{target_date}_{currency_code}",
                )
                crud_exchange_rate.exchange_rate.update(
                    db, db_obj=existing_rate, obj_in=update_data
                )
                logger.debug(f"Updated rate {currency_code} for {target_date}")
            else:
                create_data = ExchangeRateCreate(
                    from_currency_id=from_id,
                    to_currency_id=to_id,
                    rate=rate,
                    valid_date=target_date,
                    rate_source="ecb",
                    ecb_rate_id=f"ECB_{target_date}_{currency_code}",
                )
                crud_exchange_rate.exchange_rate.create(db, obj_in=create_data)
                logger.debug(f"Created rate {currency_code} for {target_date}")
            updated_count += 1
        except Exception as e:
            logger.error(f"Failed to create/update rate for {currency_code}: {e}")

    logger.info(f"Updated {updated_count} exchange rates for {target_date}")
    return updated_count


async def update_current_rates(db: Session) -> int:
    """Update current exchange rates, trying today and yesterday"""
    today = date.today()
    count = await update_rates_for_date(db, today)
    if count > 0:
        return count

    # Try yesterday if today has no rates
    yesterday = today - timedelta(days=1)
    return await update_rates_for_date(db, yesterday)


async def update_rates_for_range(
    db: Session, from_date: date, to_date: date
) -> Dict[str, int]:
    """Update exchange rates for a date range"""
    results = {}
    current_date = from_date

    # Choose appropriate URL based on range
    days_diff = (to_date - from_date).days
    if days_diff <= 90:
        url = NINETY_DAY_RATES_URL
    else:
        url = HISTORICAL_RATES_URL

    try:
        response = await fetch_xml(url)
        rates_by_date = parse_ecb_xml(response.text)

        while current_date <= to_date:
            if is_business_day(current_date) and current_date in rates_by_date:
                count = await _process_date_rates(
                    db, current_date, rates_by_date[current_date]
                )
                results[current_date.isoformat()] = count
            current_date += timedelta(days=1)

    except Exception as e:
        logger.error(f"Error updating rates for range {from_date} to {to_date}: {e}")
        # Fallback to individual date updates
        current_date = from_date
        while current_date <= to_date:
            if is_business_day(current_date):
                count = await update_rates_for_date(db, current_date)
                results[current_date.isoformat()] = count
            current_date += timedelta(days=1)

    return results


async def _process_date_rates(
    db: Session, target_date: date, daily_rates: Dict[str, Decimal]
) -> int:
    """Process rates for a specific date from pre-fetched data"""
    base_currency = get_base_currency(db)
    if not base_currency:
        return 0

    is_eur_base = base_currency.code == "EUR"
    eur_currency = get_currency_by_code(db, "EUR")
    if not eur_currency:
        return 0

    updated_count = 0
    for currency_code, rate_value in daily_rates.items():
        if not is_currency_supported(currency_code):
            continue

        foreign_currency = get_currency_by_code(db, currency_code)
        if not foreign_currency:
            continue

        # Calculate rate based on base currency
        if is_eur_base:
            rate = rate_value
            from_id = eur_currency.id
            to_id = foreign_currency.id
        else:
            if base_currency.code == "BGN":
                bgn_to_foreign = FIXED_EUR_BGN / rate_value
                rate = bgn_to_foreign
                from_id = foreign_currency.id
                to_id = base_currency.id
            else:
                rate = rate_value
                from_id = eur_currency.id
                to_id = foreign_currency.id

        # Create or update rate
        existing_rate = db.exec(
            select(ExchangeRate).where(
                ExchangeRate.from_currency_id == from_id,
                ExchangeRate.to_currency_id == to_id,
                ExchangeRate.valid_date == target_date,
            )
        ).first()

        try:
            if existing_rate:
                update_data = ExchangeRateUpdate(
                    rate=rate,
                    rate_source="ecb",
                    ecb_rate_id=f"ECB_{target_date}_{currency_code}",
                )
                crud_exchange_rate.exchange_rate.update(
                    db, db_obj=existing_rate, obj_in=update_data
                )
            else:
                create_data = ExchangeRateCreate(
                    from_currency_id=from_id,
                    to_currency_id=to_id,
                    rate=rate,
                    valid_date=target_date,
                    rate_source="ecb",
                    ecb_rate_id=f"ECB_{target_date}_{currency_code}",
                )
                crud_exchange_rate.exchange_rate.create(db, obj_in=create_data)
            updated_count += 1
        except Exception as e:
            logger.error(f"Failed to process rate for {currency_code}: {e}")

    return updated_count


class ECBRateService:
    """High-level service for ECB rate management"""

    def __init__(self):
        self.timeout = 30

    async def sync_daily_rates(self, db: Session) -> Dict[str, int]:
        """Sync daily rates from ECB"""
        results = {}

        # Update today's rates
        today_count = await update_current_rates(db)
        results["today"] = today_count

        # Update last 5 business days if needed
        for i in range(1, 6):
            past_date = date.today() - timedelta(days=i)
            if is_business_day(past_date):
                count = await update_rates_for_date(db, past_date)
                results[past_date.isoformat()] = count

        return results

    async def sync_historical_rates(
        self, db: Session, days_back: int = 90
    ) -> Dict[str, int]:
        """Sync historical rates for specified number of days"""
        end_date = date.today()
        start_date = date.fromordinal(end_date.toordinal() - days_back)

        return await update_rates_for_range(db, start_date, end_date)

    def get_rate_status(self, db: Session) -> Dict[str, any]:
        """Get status of exchange rates in database"""
        base_currency = get_base_currency(db)
        latest_date = db.exec(
            select(ExchangeRate.valid_date)
            .where(ExchangeRate.rate_source == "ecb")
            .order_by(ExchangeRate.valid_date.desc())
            .limit(1)
        ).first()

        total_rates = db.exec(
            select(ExchangeRate).where(ExchangeRate.rate_source == "ecb")
        ).count()

        return {
            "base_currency": base_currency.code if base_currency else None,
            "latest_rate_date": latest_date,
            "total_ecb_rates": total_rates,
            "supported_currencies": get_supported_currencies(),
        }


# Singleton instance
ecb_rate_service = ECBRateService()
