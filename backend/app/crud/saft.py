from app.crud.base import CRUDBase
from app.models.saft import SAFT
from app.schemas.saft import SAFTCreate, SAFTUpdate


class CRUDSAFT(CRUDBase[SAFT, SAFTCreate, SAFTUpdate]):
    pass


saft = CRUDSAFT(SAFT)
