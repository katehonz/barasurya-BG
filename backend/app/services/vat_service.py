import io
from datetime import date
from typing import TextIO, Any
from decimal import Decimal

from sqlmodel import Session, select

from app.models.organization import Organization
from app.models.invoice import Invoice
from app.models.vat_sales_register import VatSalesRegister
from app.models.vat_purchase_register import VatPurchaseRegister


class VatService:
    def __init__(self, organization: Organization, year: int, month: int | None = None, session: Session = None):
        self.organization = organization
        self.year = year
        self.month = month
        self.session = session # Dependency injection for session

    def _format_field(self, value: Any, length: int, align: str = "left", fill_char: str = " ") -> str:
        """Helper to format fields for fixed-width output."""
        if value is None:
            value = ""
        s_value = str(value)
        if len(s_value) > length:
            s_value = s_value[:length] # Truncate if too long

        if align == "left":
            return s_value.ljust(length, fill_char)
        elif align == "right":
            return s_value.rjust(length, fill_char)
        return s_value.center(length, fill_char)

    def _format_numeric(self, value: Decimal | None, length: int, decimal_places: int = 2) -> str:
        """Helper to format numeric fields (right-aligned, dot as decimal separator)."""
        if value is None:
            value = Decimal(0)
        
        # Ensure value is Decimal
        if not isinstance(value, Decimal):
            value = Decimal(str(value))

        s_value = str(value.quantize(Decimal("0." + "0" * decimal_places))) # Format decimal places
        
        # Replace comma with dot if locale uses comma
        s_value = s_value.replace(",", ".") 

        return self._format_field(s_value, length, "right", " ")

    def _format_date(self, value: date | None) -> str:
        """Helper to format date fields as DD/MM/YYYY."""
        if value is None:
            return "          " # 10 spaces for DD/MM/YYYY
        return value.strftime("%d/%m/%Y")

class VatService:
    def __init__(self, organization: Organization, year: int, month: int | None = None, session: Session = None):
        self.organization = organization
        self.year = year
        self.month = month
        self.session = session # Dependency injection for session

    def _format_field(self, value: Any, length: int, align: str = "left", fill_char: str = " ") -> str:
        """Helper to format fields for fixed-width output."""
        if value is None:
            value = ""
        s_value = str(value)
        if len(s_value) > length:
            s_value = s_value[:length] # Truncate if too long

        if align == "left":
            return s_value.ljust(length, fill_char)
        elif align == "right":
            return s_value.rjust(length, fill_char)
        return s_value.center(length, fill_char)

    def _format_numeric(self, value: Decimal | None, length: int, decimal_places: int = 2) -> str:
        """Helper to format numeric fields (right-aligned, dot as decimal separator)."""
        if value is None:
            value = Decimal(0)
        
        # Ensure value is Decimal
        if not isinstance(value, Decimal):
            value = Decimal(str(value))

        s_value = str(value.quantize(Decimal("0." + "0" * decimal_places))) # Format decimal places
        
        # Replace comma with dot if locale uses comma
        s_value = s_value.replace(",", ".") 

        return self._format_field(s_value, length, "right", " ")

    def _format_date(self, value: date | None) -> str:
        """Helper to format date fields as DD/MM/YYYY."""
        if value is None:
            return "          " # 10 spaces for DD/MM/YYYY
        return value.strftime("%d/%m/%Y")

    def generate_sales_register(self, output: TextIO):
        """Generates the PRODAGBI.TXT file (Sales Register)."""
        if not self.session:
            raise ValueError("Session is required for VAT report generation.")

        # Fetch sales register entries for the period
        statement = select(VatSalesRegister).where(
            VatSalesRegister.organization_id == self.organization.id,
            VatSalesRegister.period_year == self.year,
            VatSalesRegister.period_month == self.month,
        ).order_by(VatSalesRegister.document_date) # Order by date as per spec

        sales_entries = self.session.exec(statement).all()

        for index, entry in enumerate(sales_entries):
            line = []
            # 1. Номер по ред на документа в дневника (15 цифри, дясно изравнен)
            line.append(self._format_field(str(index + 1), 15, "right")) 
            # 2. Вид на документа (2 символа)
            line.append(self._format_field(entry.document_type, 2)) 
            # 3. Номер на документа (20 символа)
            line.append(self._format_field(entry.document_number, 20))
            # 4. Дата на издаване на документа (10 символа - ДД/ММ/ГГГГ)
            line.append(self._format_date(entry.document_date))
            # 5. ДДС номер на контрагента (15 символа)
            line.append(self._format_field(entry.recipient_vat_number or "", 15)) 
            # 6. Име на контрагента (70 символа)
            line.append(self._format_field(entry.recipient_name, 70))
            # 7. Данъчна основа за облагаеми доставки със ставка 20 % (15 цифри, 2 десетични знака)
            line.append(self._format_numeric(entry.taxable_base, 15, 2))
            # 8. Начислен ДДС 20 % (15 цифри, 2 десетични знака)
            line.append(self._format_numeric(entry.vat_amount, 15, 2))
            
            # Simplified line output for now
            output.write("".join(line) + "\n")

    def generate_purchase_register(self, output: TextIO):
        """Generates the POKUPKI.TXT file (Purchase Register)."""
        if not self.session:
            raise ValueError("Session is required for VAT report generation.")

        # Fetch purchase register entries for the period
        statement = select(VatPurchaseRegister).where(
            VatPurchaseRegister.organization_id == self.organization.id,
            VatPurchaseRegister.period_year == self.year,
            VatPurchaseRegister.period_month == self.month,
        ).order_by(VatPurchaseRegister.document_date) # Order by date as per spec

        purchase_entries = self.session.exec(statement).all()

        for index, entry in enumerate(purchase_entries):
            line = []
            # 1. Номер по ред на документа в дневника (15 цифри, дясно изравнен)
            line.append(self._format_field(str(index + 1), 15, "right")) 
            # 2. Вид на документа (2 символа)
            line.append(self._format_field(entry.document_type, 2)) 
            # 3. Номер на документа (20 символа)
            line.append(self._format_field(entry.document_number, 20))
            # 4. Дата на издаване на документа (10 символа - ДД/ММ/ГГГГ)
            line.append(self._format_date(entry.document_date))
            # 5. ДДС номер на контрагента (15 символа)
            line.append(self._format_field(entry.supplier_vat_number or "", 15)) 
            # 6. Име на контрагента (70 символа)
            line.append(self._format_field(entry.supplier_name, 70))
            # 7. Данъчна основа за облагаеми доставки със ставка 20 % (15 цифри, 2 десетични знака)
            line.append(self._format_numeric(entry.taxable_base, 15, 2))
            # 8. Начислен ДДС 20 % (15 цифри, 2 десетични знака)
            line.append(self._format_numeric(entry.vat_amount, 15, 2))
            
            # Simplified line output for now
            output.write("".join(line) + "\n")

    def generate_vat_declaration(self, output: TextIO):
        """Generates the DEKLAR.TXT file (VAT Declaration)."""
        if not self.session:
            raise ValueError("Session is required for VAT report generation.")

        # Fetch all sales and purchase register entries for the period to calculate totals
        sales_statement = select(VatSalesRegister).where(
            VatSalesRegister.organization_id == self.organization.id,
            VatSalesRegister.period_year == self.year,
            VatSalesRegister.period_month == self.month,
        )
        sales_entries = self.session.exec(sales_statement).all()

        purchase_statement = select(VatPurchaseRegister).where(
            VatPurchaseRegister.organization_id == self.organization.id,
            VatPurchaseRegister.period_year == self.year,
            VatPurchaseRegister.period_month == self.month,
        )
        purchase_entries = self.session.exec(purchase_statement).all()

        # Initialize totals
        total_sales_taxable_base = Decimal(0)
        total_sales_vat_amount = Decimal(0)
        total_purchase_taxable_base = Decimal(0)
        total_purchase_vat_amount = Decimal(0)

        # Calculate sales totals
        for entry in sales_entries:
            total_sales_taxable_base += entry.taxable_base
            total_sales_vat_amount += entry.vat_amount
        
        # Calculate purchase totals
        for entry in purchase_entries:
            total_purchase_taxable_base += entry.taxable_base
            total_purchase_vat_amount += entry.vat_amount

        # DEKLAR.TXT structure (simplified for now)
        line = []
        # 00-01 Идентификационен номер по ДДС на лицето (15 символа)
        line.append(self._format_field(self.organization.vat_number or "", 15))
        # 00-02 Наименование на лицето (50 символа)
        line.append(self._format_field(self.organization.name or "", 50))
        # 00-03 Данъчен период ГГГГММ (6 символа)
        line.append(self._format_field(f"{self.year}{self.month:02d}", 6))
        # 00-04 Лице, подаващо данните (50 символа)
        line.append(self._format_field(self.organization.legal_representative_name or "", 50))
        # 00-05 Брой документи в дневника за продажби (15 цифри)
        line.append(self._format_numeric(len(sales_entries), 15, 0))
        # 00-06 Брой документи в дневника за покупки (15 цифри)
        line.append(self._format_numeric(len(purchase_entries), 15, 0))

        # Placeholder for Sales totals (01-01 to 01-19, 01-20 to 01-24)
        # These fields are complex and depend on specific VAT rules and categories
        # For demonstration, I'll use aggregated totals
        
        # *01-01 Общ размер на данъчните основи за облагане с ДДС (15 цифри)
        line.append(self._format_numeric(total_sales_taxable_base, 15, 2))
        # *01-20 Всичко начислен ДДС (15 цифри)
        line.append(self._format_numeric(total_sales_vat_amount, 15, 2))

        # Placeholder for Purchase totals (01-30 to 01-32, 01-41 to 01-43)
        # *01-30 Данъчна основа и данък на получените доставки... (15 цифри)
        line.append(self._format_numeric(total_purchase_taxable_base, 15, 2))
        # *01-41 Начислен ДДС с право на пълен данъчен кредит (15 цифри)
        line.append(self._format_numeric(total_purchase_vat_amount, 15, 2))


        output.write("".join(line) + "\n")

