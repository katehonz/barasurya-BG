from app.crud.base import CRUDBase
from app.models.journal_entry import JournalEntry, JournalEntryLine
from app.schemas.journal_entry import JournalEntryCreate, JournalEntryUpdate
from sqlalchemy.orm import Session

class CRUDJournalEntry(CRUDBase[JournalEntry, JournalEntryCreate, JournalEntryUpdate]):
    def create(self, db: Session, *, obj_in: JournalEntryCreate) -> JournalEntry:
        db_obj = JournalEntry(
            date=obj_in.date,
            description=obj_in.description,
            currency_code=obj_in.currency_code,
            exchange_rate=obj_in.exchange_rate,
        )
        db.add(db_obj)
        db.flush()

        for line in obj_in.lines:
            db_line = JournalEntryLine(
                journal_entry_id=db_obj.id,
                **line.dict()
            )
            db.add(db_line)

        db.commit()
        db.refresh(db_obj)
        return db_obj

journal_entry = CRUDJournalEntry(JournalEntry)
