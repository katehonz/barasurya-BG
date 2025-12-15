from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app import crud
from app.api import deps
from app.schemas.saft import SAFT, SAFTCreate

router = APIRouter()


@router.get("/", response_model=list[SAFT])
def read_safts(
    db: Session = Depends(deps.get_db),
    skip: int = 0,
    limit: int = 100,
):
    """
    Retrieve SAFT reports.
    """
    safts = crud.saft.get_multi(db, skip=skip, limit=limit)
    return safts


@router.post("/", response_model=SAFT)
def create_saft(
    *,
    db: Session = Depends(deps.get_db),
    saft_in: SAFTCreate,
):
    """
    Create new SAFT report.
    """
    saft = crud.saft.create(db, obj_in=saft_in)
    return saft
