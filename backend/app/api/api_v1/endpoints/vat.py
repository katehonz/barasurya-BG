from fastapi import APIRouter, Depends
from sqlalchemy..orm import Session

from app import crud
from app.api import deps
from app.schemas.vat import VAT, VATCreate

router = APIRouter()


@router.get("/", response_model=list[VAT])
def read_vats(
    db: Session = Depends(deps.get_db),
    skip: int = 0,
    limit: int = 100,
):
    """
    Retrieve VAT reports.
    """
    vats = crud.vat.get_multi(db, skip=skip, limit=limit)
    return vats


@router.post("/", response_model=VAT)
def create_vat(
    *,
    db: Session = Depends(deps.get_db),
    vat_in: VATCreate,
):
    """
    Create new VAT report.
    """
    vat = crud.vat.create(db, obj_in=vat_in)
    return vat
