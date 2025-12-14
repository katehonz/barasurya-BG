from decimal import Decimal
from typing import List
import uuid

from sqlmodel import Session, select, func

from app.models import (
    Invoice,
    InvoiceCreate,
    InvoiceLine,
    InvoiceLineCreate,
    User,
    Organization,
)


def create_invoice(
    *,
    session: Session,
    invoice_in: InvoiceCreate,
    organization: Organization,
    user: User,
) -> Invoice:
    """
    Create a new invoice.
    """
    invoice_lines_data = []
    invoice_subtotal = Decimal(0)
    invoice_tax_amount = Decimal(0)
    line_no = 1

    for line_in in invoice_in.invoice_lines:
        line_subtotal = line_in.quantity * line_in.unit_price * (
            Decimal(1) - line_in.discount_percent / Decimal(100)
        )
        line_tax_amount = line_subtotal * (line_in.tax_rate / Decimal(100))
        line_total_amount = line_subtotal + line_tax_amount

        invoice_subtotal += line_subtotal
        invoice_tax_amount += line_tax_amount

        line_data = line_in.model_dump()
        line_data.update(
            {
                "subtotal": line_subtotal,
                "tax_amount": line_tax_amount,
                "total_amount": line_total_amount,
                "organization_id": organization.id,
                "created_by_id": user.id,
                "line_no": line_no,
            }
        )
        invoice_lines_data.append(line_data)
        line_no += 1

    invoice_total_amount = invoice_subtotal + invoice_tax_amount

    invoice_data = invoice_in.model_dump(exclude={"invoice_lines"})
    invoice_data.update(
        {
            "subtotal": invoice_subtotal,
            "tax_amount": invoice_tax_amount,
            "total_amount": invoice_total_amount,
            "organization_id": organization.id,
            "created_by_id": user.id,
        }
    )

    db_invoice = Invoice.model_validate(invoice_data)

    db_invoice_lines = [
        InvoiceLine.model_validate(line_data) for line_data in invoice_lines_data
    ]
    db_invoice.invoice_lines = db_invoice_lines

    session.add(db_invoice)
    session.commit()
    session.refresh(db_invoice)

    return db_invoice


def get_invoice(*, session: Session, invoice_id: uuid.UUID, organization: Organization) -> Invoice | None:
    """
    Get an invoice by ID.
    """
    statement = select(Invoice).where(
        Invoice.id == invoice_id, Invoice.organization_id == organization.id
    )
    return session.exec(statement).first()


def get_invoices(
    *, session: Session, organization: Organization, skip: int = 0, limit: int = 100
) -> List[Invoice]:
    """
    Get all invoices for an organization.
    """
    statement = (
        select(Invoice)
        .where(Invoice.organization_id == organization.id)
        .offset(skip)
        .limit(limit)
    )
    return session.exec(statement).all()


def count_invoices(*, session: Session, organization: Organization) -> int:
    """
    Count all invoices for an organization.
    """
    statement = select(func.count(Invoice.id)).where(
        Invoice.organization_id == organization.id
    )
    return session.exec(statement).one()
