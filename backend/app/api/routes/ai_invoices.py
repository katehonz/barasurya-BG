from fastapi import APIRouter, Depends, UploadFile, File, HTTPException, Form
from fastapi.responses import JSONResponse
from typing import List, Optional
from uuid import UUID
import uuid

from app.api.deps import get_current_user, get_db
from app.models.user import User
from app.models.extracted_invoice import (
    ExtractedInvoice,
    ExtractedInvoiceStatus,
    ExtractedInvoiceType,
)
from app.models.organization import Organization
from app.services.ai_invoice_service import invoice_processing_service
from sqlmodel import Session, select

router = APIRouter()


@router.post("/upload")
async def upload_invoice(
    file: UploadFile = File(...),
    invoice_type: ExtractedInvoiceType = Form(ExtractedInvoiceType.PURCHASE),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Upload and process invoice file with AI extraction.

    Args:
        file: PDF file of invoice
        invoice_type: Type of invoice (sales/purchase)
        current_user: Current authenticated user
        db: Database session

    Returns:
        ExtractedInvoice: Processed invoice data
    """

    # Validate file type
    if not file.content_type == "application/pdf":
        raise HTTPException(status_code=400, detail="Only PDF files are supported")

    # Get user's organization
    organization = db.exec(
        select(Organization).where(Organization.id == current_user.organization_id)
    ).first()
    if not organization:
        raise HTTPException(status_code=404, detail="Organization not found")

    try:
        extracted_invoice = await invoice_processing_service.process_invoice_upload(
            db=db,
            file=file,
            organization_id=organization.id,
            user_id=current_user.id,
            invoice_type=invoice_type,
        )

        return extracted_invoice

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/")
async def list_extracted_invoices(
    status: Optional[ExtractedInvoiceStatus] = None,
    limit: int = 100,
    offset: int = 0,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    List extracted invoices for current user's organization.

    Args:
        status: Filter by status
        limit: Number of items to return
        offset: Number of items to skip
        current_user: Current authenticated user
        db: Database session

    Returns:
        List[ExtractedInvoice]: List of extracted invoices
    """

    invoices = invoice_processing_service.get_extracted_invoices(
        db=db,
        organization_id=current_user.organization_id,
        status=status,
        limit=limit,
        offset=offset,
    )

    return invoices


@router.get("/{invoice_id}")
async def get_extracted_invoice(
    invoice_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Get specific extracted invoice by ID.

    Args:
        invoice_id: UUID of extracted invoice
        current_user: Current authenticated user
        db: Database session

    Returns:
        ExtractedInvoice: Extracted invoice details
    """

    # Get invoice with organization check
    invoice = db.exec(
        select(ExtractedInvoice).where(
            ExtractedInvoice.id == invoice_id,
            ExtractedInvoice.organization_id == current_user.organization_id,
        )
    ).first()

    if not invoice:
        raise HTTPException(status_code=404, detail="Extracted invoice not found")

    return invoice


@router.post("/{invoice_id}/approve")
async def approve_extracted_invoice(
    invoice_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Approve extracted invoice and convert to actual invoice.

    Args:
        invoice_id: UUID of extracted invoice
        current_user: Current authenticated user
        db: Database session

    Returns:
        ExtractedInvoice: Approved invoice
    """

    # Check ownership
    invoice = db.exec(
        select(ExtractedInvoice).where(
            ExtractedInvoice.id == invoice_id,
            ExtractedInvoice.organization_id == current_user.organization_id,
        )
    ).first()

    if not invoice:
        raise HTTPException(status_code=404, detail="Extracted invoice not found")

    try:
        approved_invoice = await invoice_processing_service.approve_extracted_invoice(
            db=db, extracted_invoice_id=invoice_id, user_id=current_user.id
        )

        return approved_invoice

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{invoice_id}/reject")
async def reject_extracted_invoice(
    invoice_id: UUID,
    rejection_reason: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Reject extracted invoice.

    Args:
        invoice_id: UUID of extracted invoice
        rejection_reason: Reason for rejection
        current_user: Current authenticated user
        db: Database session

    Returns:
        ExtractedInvoice: Rejected invoice
    """

    # Check ownership
    invoice = db.exec(
        select(ExtractedInvoice).where(
            ExtractedInvoice.id == invoice_id,
            ExtractedInvoice.organization_id == current_user.organization_id,
        )
    ).first()

    if not invoice:
        raise HTTPException(status_code=404, detail="Extracted invoice not found")

    try:
        rejected_invoice = await invoice_processing_service.reject_extracted_invoice(
            db=db,
            extracted_invoice_id=invoice_id,
            user_id=current_user.id,
            rejection_reason=rejection_reason,
        )

        return rejected_invoice

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/stats/summary")
async def get_processing_stats(
    current_user: User = Depends(get_current_user), db: Session = Depends(get_db)
):
    """
    Get processing statistics for current organization.

    Args:
        current_user: Current authenticated user
        db: Database session

    Returns:
        dict: Processing statistics
    """

    # Count by status
    pending_count = db.exec(
        select(ExtractedInvoice).where(
            ExtractedInvoice.organization_id == current_user.organization_id,
            ExtractedInvoice.status == ExtractedInvoiceStatus.PENDING_REVIEW,
        )
    ).count()

    approved_count = db.exec(
        select(ExtractedInvoice).where(
            ExtractedInvoice.organization_id == current_user.organization_id,
            ExtractedInvoice.status == ExtractedInvoiceStatus.APPROVED,
        )
    ).count()

    rejected_count = db.exec(
        select(ExtractedInvoice).where(
            ExtractedInvoice.organization_id == current_user.organization_id,
            ExtractedInvoice.status == ExtractedInvoiceStatus.REJECTED,
        )
    ).count()

    total_count = db.exec(
        select(ExtractedInvoice).where(
            ExtractedInvoice.organization_id == current_user.organization_id
        )
    ).count()

    return {
        "total": total_count,
        "pending_review": pending_count,
        "approved": approved_count,
        "rejected": rejected_count,
    }
