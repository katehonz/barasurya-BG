from typing import Any
import uuid
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import Response
from app.api.deps import SessionDep, CurrentUser, CurrentOrganization
from app.models import (
    InvoiceCreate,
    InvoicePublic,
    InvoicesPublic,
)
from app.crud import invoice as crud_invoice
from app.services.pdf_service import PdfService

router = APIRouter()





@router.get("/", response_model=InvoicesPublic)

def read_invoices(

    session: SessionDep,

    current_user: CurrentUser,

    current_org: CurrentOrganization,

    skip: int = 0,

    limit: int = 100,

) -> Any:

    """

    Retrieve invoices.

    """

    invoices = crud_invoice.get_invoices(

        session=session, organization=current_org, skip=skip, limit=limit

    )

    count = crud_invoice.count_invoices(session=session, organization=current_org)



    return InvoicesPublic(data=invoices, count=count)





@router.post("/", response_model=InvoicePublic)

def create_invoice(

    *,

    session: SessionDep,

    current_user: CurrentUser,

    current_org: CurrentOrganization,

    invoice_in: InvoiceCreate,

) -> Any:

    """

    Create new invoice.

    """

    invoice = crud_invoice.create_invoice(

        session=session,

        invoice_in=invoice_in,

        organization=current_org,

        user=current_user,

    )

    return invoice


@router.get("/{id}/pdf", response_class=Response)
async def download_invoice_pdf(
    session: SessionDep,
    current_org: CurrentOrganization,
    id: uuid.UUID,
) -> Response:
    """
    Download invoice as PDF.
    """
    invoice = crud_invoice.get_invoice(session=session, organization=current_org, id=id)
    if not invoice:
        raise HTTPException(status_code=404, detail="Invoice not found")

    # TODO: this is a hack, we should have a proper way to get the invoice data
    # as a dictionary.
    invoice_data = invoice.model_dump()
    # model_dump returns UUIDs as UUID objects, but we need strings for JSON
    invoice_data["id"] = str(invoice_data["id"])
    if invoice.organization:
        invoice_data["organization_id"] = str(invoice.organization.id)
    if invoice.created_by:
        invoice_data["created_by_id"] = str(invoice.created_by.id)
    if invoice.contact:
        invoice_data["contact_id"] = str(invoice.contact.id)
    if invoice.bank_account:
        invoice_data["bank_account_id"] = str(invoice.bank_account.id)
    if invoice.parent_invoice:
        invoice_data["parent_invoice_id"] = str(invoice.parent_invoice.id)
    for line in invoice_data["invoice_lines"]:
        line["id"] = str(line["id"])
        line["invoice_id"] = str(line["invoice_id"])
        if line["product_id"]:
            line["product_id"] = str(line["product_id"])

    pdf_binary = await PdfService.generate_invoice_pdf(invoice_data)

    return Response(
        content=pdf_binary,
        media_type="application/pdf",
        headers={"Content-Disposition": f"attachment; filename=invoice-{invoice.invoice_no}.pdf"},
    )

