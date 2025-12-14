import httpx
import re
from datetime import datetime
from typing import Any, Dict, Optional
from uuid import UUID

from sqlalchemy import select
from sqlmodel.ext.asyncio.session import AsyncSession

from app.core.config import settings
from app.models.contraagent import Contraagent, ContraagentCreate, ContraagentUpdate
from app.models.contraagent_bank_account import (
    ContraagentBankAccount,
    ContraagentBankAccountCreate,
    ContraagentBankAccountUpdate,
)


class VIESValidator:
    """EU VIES VAT Information Exchange System validator"""

    VIES_API_URL = "https://ec.europa.eu/taxation_customs/vies/rest-api/ms"

    @staticmethod
    def parse_vat_number(vat_number: str) -> Optional[Dict[str, str]]:
        """Parse VAT number to extract country code and number"""
        if not vat_number:
            return None

        # Remove spaces and special characters
        vat_clean = re.sub(r"[^\w]", "", vat_number.upper())

        # Extract country code (first 2 letters)
        if len(vat_clean) < 3:
            return None

        country_code = vat_clean[:2]
        number = vat_clean[2:]

        return {
            "country_code": country_code,
            "number": number,
            "full_vat": f"{country_code}{number}",
        }

    @staticmethod
    def extract_bulgarian_eik(vat_number: str) -> Optional[str]:
        """Extract Bulgarian EIK from BG VAT number"""
        parsed = VIESValidator.parse_vat_number(vat_number)
        if not parsed or parsed["country_code"] != "BG":
            return None

        # Bulgarian VAT numbers are BG + EIK (9 or 13 digits)
        eik = parsed["number"]
        if len(eik) in [9, 13] and eik.isdigit():
            return eik

        return None

    @staticmethod
    async def validate_vat(vat_number: str) -> Dict[str, Any]:
        """Validate VAT number using EU VIES API"""
        if not vat_number:
            return {"valid": False, "error": "VAT number is required"}

        parsed = VIESValidator.parse_vat_number(vat_number)
        if not parsed:
            return {"valid": False, "error": "Invalid VAT number format"}

        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                url = f"{VIESValidator.VIES_API_URL}/{parsed['country_code']}/{parsed['number']}"

                response = await client.get(url)

                if response.status_code == 200:
                    data = response.json()

                    if data.get("isValid"):
                        return {
                            "valid": True,
                            "country_code": parsed["country_code"],
                            "vat_number": parsed["full_vat"],
                            "company_name": data.get("name"),
                            "address": data.get("address"),
                            "request_date": data.get("requestDate"),
                            "eik": VIESValidator.extract_bulgarian_eik(vat_number),
                        }
                    else:
                        return {
                            "valid": False,
                            "error": "VAT number not found in VIES database",
                            "country_code": parsed["country_code"],
                            "vat_number": parsed["full_vat"],
                        }
                else:
                    return {
                        "valid": False,
                        "error": f"VIES API error: {response.status_code}",
                        "country_code": parsed["country_code"],
                        "vat_number": parsed["full_vat"],
                    }

        except httpx.TimeoutException:
            return {
                "valid": False,
                "error": "VIES service timeout - please try again later",
                "country_code": parsed["country_code"],
                "vat_number": parsed["full_vat"],
            }
        except Exception as e:
            return {
                "valid": False,
                "error": f"Validation error: {str(e)}",
                "country_code": parsed["country_code"],
                "vat_number": parsed["full_vat"],
            }


class ContraagentService:
    """Service for managing contraagents with VAT VIES validation"""

    @staticmethod
    async def get_contraagents(
        session: AsyncSession,
        organization_id: UUID,
        skip: int = 0,
        limit: int = 100,
        search: Optional[str] = None,
        is_customer: Optional[bool] = None,
        is_supplier: Optional[bool] = None,
        is_active: Optional[bool] = None,
    ) -> tuple[list[Contraagent], int]:
        """Get contraagents with filtering and pagination"""

        query = select(Contraagent).where(
            Contraagent.organization_id == organization_id
        )

        if search:
            search_term = f"%{search}%"
            query = query.where(
                (Contraagent.name.ilike(search_term))
                | (Contraagent.vat_number.ilike(search_term))
                | (Contraagent.registration_number.ilike(search_term))
                | (Contraagent.email.ilike(search_term))
            )

        if is_customer is not None:
            query = query.where(Contraagent.is_customer == is_customer)

        if is_supplier is not None:
            query = query.where(Contraagent.is_supplier == is_supplier)

        if is_active is not None:
            query = query.where(Contraagent.is_active == is_active)

        # Get total count
        count_query = select(Contraagent).where(
            Contraagent.organization_id == organization_id
        )
        if search:
            search_term = f"%{search}%"
            count_query = count_query.where(
                (Contraagent.name.ilike(search_term))
                | (Contraagent.vat_number.ilike(search_term))
                | (Contraagent.registration_number.ilike(search_term))
                | (Contraagent.email.ilike(search_term))
            )
        if is_customer is not None:
            count_query = count_query.where(Contraagent.is_customer == is_customer)
        if is_supplier is not None:
            count_query = count_query.where(Contraagent.is_supplier == is_supplier)
        if is_active is not None:
            count_query = count_query.where(Contraagent.is_active == is_active)

        count_result = await session.exec(count_query)
        total = len(count_result.all())

        # Get paginated results
        query = query.order_by(Contraagent.name).offset(skip).limit(limit)
        result = await session.exec(query)
        contraagents = result.all()

        return contraagents, total

    @staticmethod
    async def get_contraagent_by_id(
        session: AsyncSession, organization_id: UUID, contraagent_id: UUID
    ) -> Optional[Contraagent]:
        """Get contraagent by ID"""
        query = select(Contraagent).where(
            Contraagent.id == contraagent_id,
            Contraagent.organization_id == organization_id,
        )
        result = await session.exec(query)
        return result.first()

    @staticmethod
    async def get_contraagent_by_vat_number(
        session: AsyncSession, organization_id: UUID, vat_number: str
    ) -> Optional[Contraagent]:
        """Get contraagent by VAT number"""
        query = select(Contraagent).where(
            Contraagent.vat_number == vat_number,
            Contraagent.organization_id == organization_id,
        )
        result = await session.exec(query)
        return result.first()

    @staticmethod
    async def create_contraagent(
        session: AsyncSession,
        organization_id: UUID,
        created_by_id: UUID,
        contraagent_create: ContraagentCreate,
        validate_vat: bool = True,
    ) -> tuple[Contraagent, Optional[Dict[str, Any]]]:
        """Create new contraagent with optional VAT validation"""

        # VAT validation if requested and VAT number provided
        vat_validation = None
        if validate_vat and contraagent_create.vat_number:
            vat_validation = await VIESValidator.validate_vat(
                contraagent_create.vat_number
            )

            if vat_validation["valid"]:
                # Auto-fill company name and address from VIES if available
                if vat_validation.get("company_name") and not contraagent_create.name:
                    contraagent_create.name = vat_validation["company_name"]

                if (
                    vat_validation.get("eik")
                    and not contraagent_create.registration_number
                ):
                    contraagent_create.registration_number = vat_validation["eik"]

        # Create contraagent
        contraagent = Contraagent(
            **contraagent_create.dict(),
            organization_id=organization_id,
            created_by_id=created_by_id,
        )

        session.add(contraagent)
        await session.commit()
        await session.refresh(contraagent)

        return contraagent, vat_validation

    @staticmethod
    async def update_contraagent(
        session: AsyncSession,
        organization_id: UUID,
        contraagent_id: UUID,
        contraagent_update: ContraagentUpdate,
        validate_vat: bool = True,
    ) -> tuple[Contraagent, Optional[Dict[str, Any]]]:
        """Update contraagent with optional VAT validation"""

        contraagent = await ContraagentService.get_contraagent_by_id(
            session, organization_id, contraagent_id
        )

        if not contraagent:
            raise ValueError("Contraagent not found")

        # VAT validation if VAT number is being updated
        vat_validation = None
        if (
            validate_vat
            and contraagent_update.vat_number
            and contraagent_update.vat_number != contraagent.vat_number
        ):
            vat_validation = await VIESValidator.validate_vat(
                contraagent_update.vat_number
            )

            if vat_validation["valid"]:
                # Update tax verification date
                contraagent_update.tax_verification_date = datetime.utcnow()

        # Update contraagent
        update_data = contraagent_update.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(contraagent, field, value)

        contraagent.date_updated = datetime.utcnow()

        await session.commit()
        await session.refresh(contraagent)

        return contraagent, vat_validation

    @staticmethod
    async def delete_contraagent(
        session: AsyncSession, organization_id: UUID, contraagent_id: UUID
    ) -> bool:
        """Delete contraagent (soft delete by setting is_active=False)"""

        contraagent = await ContraagentService.get_contraagent_by_id(
            session, organization_id, contraagent_id
        )

        if not contraagent:
            return False

        contraagent.is_active = False
        contraagent.date_updated = datetime.utcnow()

        await session.commit()
        return True

    @staticmethod
    async def add_bank_account(
        session: AsyncSession,
        organization_id: UUID,
        contraagent_id: UUID,
        bank_account_create: ContraagentBankAccountCreate,
    ) -> ContraagentBankAccount:
        """Add bank account to contraagent"""

        # Verify contraagent exists and belongs to organization
        contraagent = await ContraagentService.get_contraagent_by_id(
            session, organization_id, contraagent_id
        )

        if not contraagent:
            raise ValueError("Contraagent not found")

        # If setting as primary, unset other primary accounts
        if bank_account_create.is_primary:
            existing_primary = await session.exec(
                select(ContraagentBankAccount).where(
                    ContraagentBankAccount.contraagent_id == contraagent_id,
                    ContraagentBankAccount.is_primary == True,
                )
            )
            for account in existing_primary:
                account.is_primary = False

        bank_account = ContraagentBankAccount(
            **bank_account_create.dict(), contraagent_id=contraagent_id
        )

        session.add(bank_account)
        await session.commit()
        await session.refresh(bank_account)

        return bank_account

    @staticmethod
    async def update_bank_account(
        session: AsyncSession,
        organization_id: UUID,
        bank_account_id: UUID,
        bank_account_update: ContraagentBankAccountUpdate,
    ) -> ContraagentBankAccount:
        """Update contraagent bank account"""

        # Get bank account with contraagent verification
        query = (
            select(ContraagentBankAccount)
            .join(Contraagent)
            .where(
                ContraagentBankAccount.id == bank_account_id,
                Contraagent.organization_id == organization_id,
            )
        )
        result = await session.exec(query)
        bank_account = result.first()

        if not bank_account:
            raise ValueError("Bank account not found")

        # If setting as primary, unset other primary accounts
        if bank_account_update.is_primary and not bank_account.is_primary:
            existing_primary = await session.exec(
                select(ContraagentBankAccount).where(
                    ContraagentBankAccount.contraagent_id
                    == bank_account.contraagent_id,
                    ContraagentBankAccount.is_primary == True,
                    ContraagentBankAccount.id != bank_account_id,
                )
            )
            for account in existing_primary:
                account.is_primary = False

        # Update bank account
        update_data = bank_account_update.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(bank_account, field, value)

        bank_account.date_updated = datetime.utcnow()

        await session.commit()
        await session.refresh(bank_account)

        return bank_account

    @staticmethod
    async def delete_bank_account(
        session: AsyncSession, organization_id: UUID, bank_account_id: UUID
    ) -> bool:
        """Delete contraagent bank account"""

        # Get bank account with contraagent verification
        query = (
            select(ContraagentBankAccount)
            .join(Contraagent)
            .where(
                ContraagentBankAccount.id == bank_account_id,
                Contraagent.organization_id == organization_id,
            )
        )
        result = await session.exec(query)
        bank_account = result.first()

        if not bank_account:
            return False

        await session.delete(bank_account)
        await session.commit()

        return True
