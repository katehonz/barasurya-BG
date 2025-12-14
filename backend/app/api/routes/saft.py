
from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session

from app.api.deps import get_current_organization, get_db
from app.models.organization import Organization
from app.services.saft_service import SAFT
from app.services.vat_service import VatService
from starlette.responses import StreamingResponse
import io

router = APIRouter(prefix="/saft", tags=["saft"])


@router.get("/")
def generate_saft(
    *,
    session: Session = Depends(get_db),
    current_organization: Organization = Depends(get_current_organization),
    report_type: str,
    year: int,
    month: int | None = None,
):
    """
    Generate a SAF-T file.
    """
    if report_type not in ["monthly", "annual", "on_demand"]:
        raise HTTPException(status_code=400, detail="Invalid report type")

    if report_type == "monthly" and not month:
        raise HTTPException(status_code=400, detail="Month is required for monthly reports")

    saft = SAFT(organization=current_organization, year=year, month=month)
    output = io.StringIO()
    saft.generate(report_type=report_type, output=output)
    output.seek(0)

    return StreamingResponse(
        iter([output.read()]),
        media_type="application/xml",
        headers={"Content-Disposition": f"attachment; filename=saft_{report_type}.xml"},
    )


@router.get("/vat/sales-register")
def generate_vat_sales_register(
    *,
    session: Session = Depends(get_db),
    current_organization: Organization = Depends(get_current_organization),
    year: int,
    month: int,
):
    """
    Generate VAT sales register (PRODAGBI.TXT).
    """
    vat_service = VatService(organization=current_organization, year=year, month=month)
    output = io.StringIO()
    vat_service.generate_sales_register(output)
    output.seek(0)

    # Encode to CP-1251
    encoded_output = output.read().encode("cp1251")

    return StreamingResponse(
        iter([encoded_output]),
        media_type="text/plain",
        headers={
            "Content-Disposition": f"attachment; filename=PRODAGBI_{year}_{month:02d}.txt"
        },
    )


@router.get("/vat/purchase-register")
def generate_vat_purchase_register(
    *,
    session: Session = Depends(get_db),
    current_organization: Organization = Depends(get_current_organization),
    year: int,
    month: int,
):
    """
    Generate VAT purchase register (POKUPKI.TXT).
    """
    vat_service = VatService(organization=current_organization, year=year, month=month)
    output = io.StringIO()
    vat_service.generate_purchase_register(output)
    output.seek(0)

    # Encode to CP-1251
    encoded_output = output.read().encode("cp1251")

    return StreamingResponse(
        iter([encoded_output]),
        media_type="text/plain",
        headers={
            "Content-Disposition": f"attachment; filename=POKUPKI_{year}_{month:02d}.txt"
        },
    )


@router.get("/vat/declaration")
def generate_vat_declaration(
    *,
    session: Session = Depends(get_db),
    current_organization: Organization = Depends(get_current_organization),
    year: int,
    month: int,
):
    """
    Generate VAT declaration (DEKLAR.TXT).
    """
    vat_service = VatService(organization=current_organization, year=year, month=month)
    output = io.StringIO()
    vat_service.generate_vat_declaration(output)
    output.seek(0)

    # Encode to CP-1251
    encoded_output = output.read().encode("cp1251")

    return StreamingResponse(
        iter([encoded_output]),
        media_type="text/plain",
        headers={
            "Content-Disposition": f"attachment; filename=DEKLAR_{year}_{month:02d}.txt"
        },
    )
