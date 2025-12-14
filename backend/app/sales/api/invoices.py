
from typing import Any

from fastapi import APIRouter, Depends
from app.api.deps import SessionDep, CurrentUser
from app.models import (
    InvoiceCreate,
    InvoicePublic,
    InvoicesPublic,
)

router = APIRouter()


@router.get("/", response_model=InvoicesPublic)
def read_invoices(
    session: SessionDep, current_user: CurrentUser, skip: int = 0, limit: int = 100
) -> Any:
    """
    Retrieve invoices.
    """
    # TODO: Implement CRUD
    pass


@router.post("/", response_model=InvoicePublic)
def create_invoice(
    *, session: SessionDep, current_user: CurrentUser, invoice_in: InvoiceCreate
) -> Any:
    """
    Create new invoice.
    """
    # TODO: Implement CRUD
    pass

