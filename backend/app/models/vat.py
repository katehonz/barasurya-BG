from app.core.db import Base
from sqlalchemy import Column, Integer, JSON

class VAT(Base):
    id = Column(Integer, primary_key=True, index=True)
    data = Column(JSON)
