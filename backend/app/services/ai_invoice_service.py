import os
import json
import uuid
from typing import Optional, Dict, Any, List
from decimal import Decimal
from datetime import datetime, date
from azure.ai.documentintelligence import DocumentIntelligenceClient
from azure.ai.documentintelligence.models import AnalyzeDocumentRequest
from azure.core.credentials import AzureKeyCredential
from fastapi import UploadFile, HTTPException
from sqlmodel import Session, select

from app.core.config import settings
from app.models.document_upload import DocumentUpload, DocumentUploadStatus
from app.models.extracted_invoice import (
    ExtractedInvoice,
    ExtractedInvoiceStatus,
    ExtractedInvoiceType,
)
from app.models.organization import Organization
from app.models.user import User
from app.services.document_numbering_service import DocumentNumberingService


class InvoiceProcessingService:
    """Service for AI-powered invoice processing using Azure Document Intelligence."""

    def __init__(self):
        self._azure_client = None

    @property
    def azure_client(self) -> DocumentIntelligenceClient:
        """Lazy initialization of Azure client."""
        if self._azure_client is None:
            if not (
                settings.AZURE_DOCUMENT_INTELLIGENCE_ENDPOINT
                and settings.AZURE_DOCUMENT_INTELLIGENCE_KEY
            ):
                raise ValueError(
                    "Azure Document Intelligence не е конфигуриран. "
                    "Задайте AZURE_DOCUMENT_INTELLIGENCE_ENDPOINT и AZURE_DOCUMENT_INTELLIGENCE_KEY."
                )
            self._azure_client = DocumentIntelligenceClient(
                endpoint=settings.AZURE_DOCUMENT_INTELLIGENCE_ENDPOINT,
                credential=AzureKeyCredential(settings.AZURE_DOCUMENT_INTELLIGENCE_KEY),
            )
        return self._azure_client

    async def process_invoice_upload(
        self,
        db: Session,
        file: UploadFile,
        organization_id: uuid.UUID,
        user_id: uuid.UUID,
        invoice_type: ExtractedInvoiceType = ExtractedInvoiceType.PURCHASE,
    ) -> ExtractedInvoice:
        """Process uploaded invoice file and extract data."""

        # Create document upload record
        document_upload = DocumentUpload(
            organization_id=organization_id,
            created_by_id=user_id,
            original_filename=file.filename,
            file_size=file.size,
            file_type=file.content_type,
            status=DocumentUploadStatus.PENDING,
        )
        db.add(document_upload)
        db.commit()
        db.refresh(document_upload)

        try:
            # Read file content
            file_content = await file.read()

            # Process with AI
            extracted_data = await self._extract_invoice_data(file_content)

            # Create extracted invoice record
            extracted_invoice = ExtractedInvoice(
                organization_id=organization_id,
                created_by_id=user_id,
                document_upload_id=document_upload.id,
                invoice_type=invoice_type,
                status=ExtractedInvoiceStatus.PENDING_REVIEW,
                confidence_score=Decimal(
                    str(extracted_data.get("confidence_score", 0.0))
                ),
                invoice_number=extracted_data.get("invoice_number"),
                invoice_date=self._parse_date(extracted_data.get("invoice_date")),
                due_date=self._parse_date(extracted_data.get("due_date")),
                vendor_name=extracted_data.get("vendor_name"),
                vendor_address=extracted_data.get("vendor_address"),
                vendor_vat_number=extracted_data.get("vendor_vat_number"),
                customer_name=extracted_data.get("customer_name"),
                customer_address=extracted_data.get("customer_address"),
                customer_vat_number=extracted_data.get("customer_vat_number"),
                subtotal=self._parse_decimal(extracted_data.get("subtotal")),
                tax_amount=self._parse_decimal(extracted_data.get("tax_amount")),
                total_amount=self._parse_decimal(extracted_data.get("total_amount")),
                currency=extracted_data.get("currency", "BGN"),
                line_items=extracted_data.get("line_items", []),
                raw_data=extracted_data.get("raw_data", {}),
                oss_country=extracted_data.get("oss_country"),
                oss_vat_rate=self._parse_decimal(extracted_data.get("oss_vat_rate")),
            )

            db.add(extracted_invoice)

            # Update document upload status
            document_upload.status = DocumentUploadStatus.COMPLETED
            document_upload.processed_at = datetime.utcnow()
            document_upload.azure_result = extracted_data.get("raw_data", {})

            db.commit()
            db.refresh(extracted_invoice)

            return extracted_invoice

        except Exception as e:
            # Update document upload with error
            document_upload.status = DocumentUploadStatus.FAILED
            document_upload.error_message = str(e)
            db.commit()
            raise HTTPException(
                status_code=500, detail=f"Failed to process invoice: {str(e)}"
            )

    async def _extract_invoice_data(self, file_content: bytes) -> Dict[str, Any]:
        """Extract invoice data using Azure Document Intelligence."""
        return await self._extract_with_azure(file_content)

    async def _extract_with_azure(self, file_content: bytes) -> Dict[str, Any]:
        """Extract invoice data using Azure Document Intelligence."""

        try:
            # Analyze document
            poller = self.azure_client.begin_analyze_document(
                "prebuilt-invoice",
                analyze_request=file_content,
                content_type="application/octet-stream",
            )

            # Wait for result
            result = poller.result()

            # Extract structured data
            extracted_data = {
                "confidence_score": self._calculate_azure_confidence(result),
                "raw_data": result.as_dict(),
            }

            # Extract invoice fields
            if result.documents:
                doc = result.documents[0]

                # Basic fields
                if doc.fields.get("InvoiceId"):
                    extracted_data["invoice_number"] = doc.fields[
                        "InvoiceId"
                    ].value_string

                if doc.fields.get("InvoiceDate"):
                    extracted_data["invoice_date"] = doc.fields[
                        "InvoiceDate"
                    ].value_date

                if doc.fields.get("DueDate"):
                    extracted_data["due_date"] = doc.fields["DueDate"].value_date

                if doc.fields.get("VendorName"):
                    extracted_data["vendor_name"] = doc.fields[
                        "VendorName"
                    ].value_string

                if doc.fields.get("VendorAddress"):
                    extracted_data["vendor_address"] = doc.fields[
                        "VendorAddress"
                    ].value_string

                if doc.fields.get("VendorTaxId"):
                    extracted_data["vendor_vat_number"] = doc.fields[
                        "VendorTaxId"
                    ].value_string

                if doc.fields.get("CustomerName"):
                    extracted_data["customer_name"] = doc.fields[
                        "CustomerName"
                    ].value_string

                if doc.fields.get("CustomerAddress"):
                    extracted_data["customer_address"] = doc.fields[
                        "CustomerAddress"
                    ].value_string

                if doc.fields.get("CustomerTaxId"):
                    extracted_data["customer_vat_number"] = doc.fields[
                        "CustomerTaxId"
                    ].value_string

                # Financial fields
                if doc.fields.get("SubTotal"):
                    extracted_data["subtotal"] = float(
                        doc.fields["SubTotal"].value_currency.amount
                    )

                if doc.fields.get("TotalTax"):
                    extracted_data["tax_amount"] = float(
                        doc.fields["TotalTax"].value_currency.amount
                    )

                if doc.fields.get("InvoiceTotal"):
                    extracted_data["total_amount"] = float(
                        doc.fields["InvoiceTotal"].value_currency.amount
                    )
                    if doc.fields["InvoiceTotal"].value_currency.currency_code:
                        extracted_data["currency"] = doc.fields[
                            "InvoiceTotal"
                        ].value_currency.currency_code

                # Line items
                if doc.fields.get("Items"):
                    line_items = []
                    for item in doc.fields["Items"].value_array:
                        line_item = {}

                        if item.value_object.get("Description"):
                            line_item["description"] = item.value_object[
                                "Description"
                            ].value_string

                        if item.value_object.get("Quantity"):
                            line_item["quantity"] = float(
                                item.value_object["Quantity"].value_integer
                            )

                        if item.value_object.get("UnitPrice"):
                            line_item["unit_price"] = float(
                                item.value_object["UnitPrice"].value_currency.amount
                            )

                        if item.value_object.get("Amount"):
                            line_item["amount"] = float(
                                item.value_object["Amount"].value_currency.amount
                            )

                        if item.value_object.get("ProductCode"):
                            line_item["product_code"] = item.value_object[
                                "ProductCode"
                            ].value_string

                        if item.value_object.get("Tax"):
                            line_item["tax"] = float(
                                item.value_object["Tax"].value_currency.amount
                            )

                        line_items.append(line_item)

                    extracted_data["line_items"] = line_items

            return extracted_data

        except Exception as e:
            raise Exception(f"Azure extraction failed: {str(e)}")


    def _calculate_azure_confidence(self, result) -> float:
        """Calculate overall confidence score from Azure result."""
        if not result.documents:
            return 0.0

        doc = result.documents[0]
        confidences = []

        # Collect confidence values from fields
        for field_name, field_value in doc.fields.items():
            if hasattr(field_value, "confidence") and field_value.confidence:
                confidences.append(field_value.confidence)

        # Return average confidence or 0.0
        return sum(confidences) / len(confidences) if confidences else 0.0

    def _parse_date(self, date_value: Any) -> Optional[date]:
        """Parse date from various formats."""
        if not date_value:
            return None

        if isinstance(date_value, date):
            return date_value

        if isinstance(date_value, str):
            try:
                return datetime.fromisoformat(date_value.replace("Z", "+00:00")).date()
            except:
                return None

        if isinstance(date_value, datetime):
            return date_value.date()

        return None

    def _parse_decimal(self, value: Any) -> Optional[Decimal]:
        """Parse decimal value from various formats."""
        if not value:
            return None

        if isinstance(value, Decimal):
            return value

        if isinstance(value, (int, float)):
            return Decimal(str(value))

        if isinstance(value, str):
            try:
                return Decimal(value)
            except:
                return None

        return None

    async def approve_extracted_invoice(
        self, db: Session, extracted_invoice_id: uuid.UUID, user_id: uuid.UUID
    ) -> ExtractedInvoice:
        """Approve extracted invoice and create actual invoice."""

        extracted_invoice = db.get(ExtractedInvoice, extracted_invoice_id)
        if not extracted_invoice:
            raise HTTPException(status_code=404, detail="Extracted invoice not found")

        # TODO: Convert to actual invoice based on type
        # This would create Invoice or Purchase record

        # Update status
        extracted_invoice.status = ExtractedInvoiceStatus.APPROVED
        extracted_invoice.approved_by_id = user_id
        extracted_invoice.approved_at = datetime.utcnow()

        db.commit()
        db.refresh(extracted_invoice)

        return extracted_invoice

    async def reject_extracted_invoice(
        self,
        db: Session,
        extracted_invoice_id: uuid.UUID,
        user_id: uuid.UUID,
        rejection_reason: str,
    ) -> ExtractedInvoice:
        """Reject extracted invoice."""

        extracted_invoice = db.get(ExtractedInvoice, extracted_invoice_id)
        if not extracted_invoice:
            raise HTTPException(status_code=404, detail="Extracted invoice not found")

        extracted_invoice.status = ExtractedInvoiceStatus.REJECTED
        extracted_invoice.approved_by_id = user_id
        extracted_invoice.approved_at = datetime.utcnow()
        extracted_invoice.rejection_reason = rejection_reason

        db.commit()
        db.refresh(extracted_invoice)

        return extracted_invoice

    def get_extracted_invoices(
        self,
        db: Session,
        organization_id: uuid.UUID,
        status: Optional[ExtractedInvoiceStatus] = None,
        limit: int = 100,
        offset: int = 0,
    ) -> List[ExtractedInvoice]:
        """Get list of extracted invoices for organization."""

        query = select(ExtractedInvoice).where(
            ExtractedInvoice.organization_id == organization_id
        )

        if status:
            query = query.where(ExtractedInvoice.status == status)

        query = query.order_by(ExtractedInvoice.date_created.desc())
        query = query.offset(offset).limit(limit)

        return db.exec(query).all()


# Singleton instance
invoice_processing_service = InvoiceProcessingService()
