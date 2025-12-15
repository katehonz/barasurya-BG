from app.crud.base import CRUDBase
from app.models.vat import VAT
from app.schemas.vat import VATCreate, VATUpdate


class CRUDVAT(CRUDBase[VAT, VATCreate, VATUpdate]):
    pass


vat = CRUDVAT(VAT)
