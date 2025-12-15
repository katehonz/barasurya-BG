from pydantic import BaseModel
from typing import List, Optional

class Header(BaseModel):
    # Define header fields based on SAF-T documentation
    pass

class GeneralLedgerAccounts(BaseModel):
    # Define GeneralLedgerAccounts fields
    pass

class Customers(BaseModel):
    # Define Customers fields
    pass

class Suppliers(BaseModel):
    # Define Suppliers fields
    pass

class TaxTable(BaseModel):
    # Define TaxTable fields
    pass

class UOMTable(BaseModel):
    # Define UOMTable fields
    pass

class AnalysisTypeTable(BaseModel):
    # Define AnalysisTypeTable fields
    pass

class MovementTypeTable(BaseModel):
    # Define MovementTypeTable fields
    pass

class Products(BaseModel):
    # Define Products fields
    pass

class PhysicalStock(BaseModel):
    # Define PhysicalStock fields
    pass

class Owners(BaseModel):
    # Define Owners fields
    pass

class Assets(BaseModel):
    # Define Assets fields
    pass

class MasterFiles(BaseModel):
    general_ledger_accounts: Optional[List[GeneralLedgerAccounts]]
    customers: Optional[List[Customers]]
    suppliers: Optional[List[Suppliers]]
    tax_table: Optional[TaxTable]
    uom_table: Optional[UOMTable]
    analysis_type_table: Optional[AnalysisTypeTable]
    movement_type_table: Optional[MovementTypeTable]
    products: Optional[List[Products]]
    physical_stock: Optional[List[PhysicalStock]]
    owners: Optional[List[Owners]]
    assets: Optional[List[Assets]]

class SAFTBase(BaseModel):
    header: Header
    master_files: MasterFiles

class SAFTCreate(SAFTBase):
    pass

class SAFTUpdate(SAFTBase):
    pass

class SAFT(SAFTBase):
    id: int

    class Config:
        orm_mode = True
