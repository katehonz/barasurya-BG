from typing import Any, List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app import crud, models
from app.api import deps

router = APIRouter()


@router.get("/", response_model=List[models.JournalEntryPublic])
def read_journal_entries(
    db: Session = Depends(deps.get_db),
    skip: int = 0,
    limit: int = 100,
) -> Any:
    """
    Retrieve journal entries.
    """
    journal_entries = crud.journal_entry.get_multi(db, skip=skip, limit=limit)
    return journal_entries


@router.post("/", response_model=models.JournalEntryPublic)
def create_journal_entry(
    *,
    db: Session = Depends(deps.get_db),
    journal_entry_in: models.JournalEntryCreate,
) -> Any:
    """
    Create new journal entry.
    """
    journal_entry = crud.journal_entry.create(db, obj_in=journal_entry_in)
    return journal_entry
