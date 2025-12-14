from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse
from app.api.deps import SessionDep, get_current_active_superuser
from app.services.vat_service import VatService
from app.models import Organization
import io

router = APIRouter()

@router.get("/sales-register")
def download_sales_register(
    session: SessionDep,
    organization: Organization = Depends(get_current_active_superuser), # This should be improved
    year: int = 2023,
    month: int = 1,
):
    """
    Download sales register as a TXT file.
    """
    output = io.StringIO()
    vat_service = VatService(organization=organization, year=year, month=month, session=session)
    vat_service.generate_sales_register(output)
    output.seek(0)
    return StreamingResponse(
        iter([output.getvalue()]),
        media_type="text/plain",
        headers={"Content-Disposition": f"attachment; filename=PRODAGBI.TXT"},
    )

@router.get("/purchase-register")
def download_purchase_register(
    session: SessionDep,
    organization: Organization = Depends(get_current_active_superuser), # This should be improved
    year: int = 2023,
    month: int = 1,
):
    """
    Download purchase register as a TXT file.
    """
    output = io.StringIO()
    vat_service = VatService(organization=organization, year=year, month=month, session=session)
    vat_service.generate_purchase_register(output)
    output.seek(0)
    return StreamingResponse(
        iter([output.getvalue()]),
        media_type="text/plain",
        headers={"Content-Disposition": f"attachment; filename=POKUPKI.TXT"},
    )

@router.get("/vat-declaration")
def download_vat_declaration(
    session: SessionDep,
    organization: Organization = Depends(get_current_active_superuser), # This should be improved
    year: int = 2023,
    month: int = 1,
):
    """
    Download VAT declaration as a TXT file.
    """
    output = io.StringIO()
    vat_service = VatService(organization=organization, year=year, month=month, session=session)
    vat_service.generate_vat_declaration(output)
    output.seek(0)
    return StreamingResponse(
        iter([output.getvalue()]),
        media_type="text/plain",
        headers={"Content-Disposition": f"attachment; filename=DEKLAR.TXT"},
    )
