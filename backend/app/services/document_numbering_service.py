"""
Document numbering service with UID patterns.
Implements sequential numbering with tenant isolation and race condition protection.
"""

import uuid
from decimal import Decimal
from typing import Optional
from datetime import datetime

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.organization import Organization
from app.utils import utcnow


class DocumentNumberingService:
    """Service for generating document numbers with proper sequencing."""

    # Document type prefixes for different document types
    DOCUMENT_PREFIXES = {
        "sales_invoice": "ИН",
        "purchase_invoice": "ФП",
        "purchase_order": "ПО",
        "quotation": "ОФ",
        "credit_note": "КН",
        "debit_note": "ДН",
        "stock_transfer": "ПС",
        "stock_adjustment": "КС",
        "proforma_invoice": "ПФ",
        "vat_protocol": "ВП",
    }

    @staticmethod
    async def get_next_number(
        db: AsyncSession,
        organization_id: uuid.UUID,
        document_type: str,
        prefix: Optional[str] = None,
    ) -> str:
        """
        Get next sequential document number for a document type.

        Args:
            db: Database session
            organization_id: Organization UUID
            document_type: Type of document (sales_invoice, purchase_order, etc.)
            prefix: Optional custom prefix

        Returns:
            Formatted document number (e.g., "ИН0000000001")
        """
        # Use provided prefix or default from document type
        if prefix is None:
            prefix = DocumentNumberingService.DOCUMENT_PREFIXES.get(document_type, "ДК")

        # Get the current sequence number from organization
        stmt = select(Organization).where(Organization.id == organization_id)
        result = await db.execute(stmt)
        org = result.scalar_one_or_none()

        if not org:
            raise ValueError(f"Organization {organization_id} not found")

        # Determine which sequence field to use
        sequence_field = f"{document_type}_next_number"

        # Use FOR UPDATE to prevent race conditions
        stmt = (
            select(Organization)
            .where(Organization.id == organization_id)
            .with_for_update()
        )
        result = await db.execute(stmt)
        org = result.scalar_one_or_none()

        if not org:
            raise ValueError(f"Organization {organization_id} not found")

        # Get current sequence number
        current_number = getattr(org, sequence_field, 1)

        # Update the sequence number for next time
        update_stmt = (
            update(Organization)
            .where(Organization.id == organization_id)
            .values({sequence_field: current_number + 1})
        )
        await db.execute(update_stmt)
        await db.commit()

        # Format as 10-digit number with leading zeros
        formatted_number = f"{current_number:010d}"

        return f"{prefix}{formatted_number}"

    @staticmethod
    async def reset_sequence(
        db: AsyncSession,
        organization_id: uuid.UUID,
        document_type: str,
        new_number: int = 1,
    ) -> None:
        """
        Reset document sequence for a document type.

        Args:
            db: Database session
            organization_id: Organization UUID
            document_type: Type of document
            new_number: New starting number
        """
        sequence_field = f"{document_type}_next_number"

        update_stmt = (
            update(Organization)
            .where(Organization.id == organization_id)
            .values({sequence_field: new_number})
        )
        await db.execute(update_stmt)
        await db.commit()

    @staticmethod
    def validate_document_number(document_number: str, document_type: str) -> bool:
        """
        Validate document number format.

        Args:
            document_number: Document number to validate
            document_type: Expected document type

        Returns:
            True if valid format
        """
        expected_prefix = DocumentNumberingService.DOCUMENT_PREFIXES.get(
            document_type, "ДК"
        )

        # Check prefix
        if not document_number.startswith(expected_prefix):
            return False

        # Check numeric part (should be 10 digits)
        numeric_part = document_number[len(expected_prefix) :]
        if len(numeric_part) != 10 or not numeric_part.isdigit():
            return False

        return True

    @staticmethod
    def extract_sequence_number(document_number: str) -> Optional[int]:
        """
        Extract sequence number from document number.

        Args:
            document_number: Document number

        Returns:
            Sequence number or None if invalid format
        """
        # Find where digits start
        i = 0
        while i < len(document_number) and not document_number[i].isdigit():
            i += 1

        if i >= len(document_number):
            return None

        numeric_part = document_number[i:]

        # Validate it's all digits
        if not numeric_part.isdigit():
            return None

        return int(numeric_part)


class DocumentUIDService:
    """Service for generating unique document identifiers."""

    @staticmethod
    def generate_document_uid(
        document_type: str,
        organization_id: uuid.UUID,
        document_number: Optional[str] = None,
    ) -> str:
        """
        Generate a unique document identifier.

        Args:
            document_type: Type of document
            organization_id: Organization UUID
            document_number: Optional document number

        Returns:
            Unique document identifier
        """
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        org_short = str(organization_id)[:8]

        if document_number:
            return f"{document_type}-{org_short}-{document_number}-{timestamp}"
        else:
            random_suffix = str(uuid.uuid4())[:8]
            return f"{document_type}-{org_short}-{timestamp}-{random_suffix}"

    @staticmethod
    def parse_document_uid(document_uid: str) -> dict:
        """
        Parse document UID to extract components.

        Args:
            document_uid: Document UID

        Returns:
            Dictionary with components
        """
        parts = document_uid.split("-")

        if len(parts) < 3:
            raise ValueError("Invalid document UID format")

        return {
            "document_type": parts[0],
            "organization_short": parts[1],
            "document_number": parts[2] if len(parts) > 3 else None,
            "timestamp": parts[-1] if len(parts) > 3 else parts[2],
            "raw": document_uid,
        }
