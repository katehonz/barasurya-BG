import html
from datetime import date, timedelta
from decimal import Decimal
from typing import IO, Any, List, Optional, Tuple
from uuid import UUID

from sqlalchemy.orm import selectinload
from sqlmodel import Session, select

from app.models.asset_transaction import AssetTransaction
from app.models.organization import Organization
from app.models.payment import Payment
from app.models.purchase import Purchase
from app.models.sale import Sale
from app.models.stock_movement import StockMovement
from app.services.saft.nomenclature import AssetMovementType, StockMovementType


class SAFTSourceDocuments:
    def __init__(self, organization: Organization, year: int, month: Optional[int] = None):
        self.organization = organization
        self.year = year
        self.month = month

    def generate(self, output: IO[Any], report_type: str, **kwargs: Any):
        if report_type == "monthly":
            content = self._build_monthly()
        elif report_type == "annual":
            content = self._build_annual()
        elif report_type == "on_demand":
            content = self._build_on_demand(**kwargs)
        else:
            raise ValueError("Invalid report type")

        output.write(content)

    def _build_monthly(self) -> str:
        return f"""
      <nsSAFT:SourceDocumentsMonthly>
    {self._build_sales_invoices()}
    {self._build_payments()}
    {self._build_purchase_invoices()}
      </nsSAFT:SourceDocumentsMonthly>
        """

    def _build_annual(self) -> str:
        return f"""
      <nsSAFT:SourceDocumentsAnnual>
    {self._build_asset_transactions()}
      </nsSAFT:SourceDocumentsAnnual>
        """

    def _build_on_demand(self, **kwargs: Any) -> str:
        return f"""
      <nsSAFT:SourceDocumentsOnDemand>
    {self._build_movement_of_goods(**kwargs)}
      </nsSAFT:SourceDocumentsOnDemand>
        """

    def _build_sales_invoices(self) -> str:
        invoices = self._get_sales_invoices()
        total_debit, total_credit = self._calculate_invoice_totals(invoices)
        invoices_xml = "\n".join([self._build_sales_invoice(invoice) for invoice in invoices])
        if not invoices:
            invoices_xml = self._build_placeholder_sales_invoice()
        return f"""
      <nsSAFT:SalesInvoices>
        <nsSAFT:NumberOfEntries>{len(invoices)}</nsSAFT:NumberOfEntries>
        <nsSAFT:TotalDebit>{self._format_decimal(total_debit)}</nsSAFT:TotalDebit>
        <nsSAFT:TotalCredit>{self._format_decimal(total_credit)}</nsSAFT:TotalCredit>
  {invoices_xml}
      </nsSAFT:SalesInvoices>
        """

    def _build_placeholder_sales_invoice(self) -> str:
        return ""

    def _build_sales_invoice(self, invoice: Any) -> str:
        lines_xml = "\n".join([self._build_invoice_line(line, i) for i, line in enumerate(invoice.lines, 1)])
        return f"""
          <nsSAFT:Invoice>
            <nsSAFT:InvoiceNo>{invoice.number}</nsSAFT:InvoiceNo>
            <nsSAFT:CustomerInfo>
              <nsSAFT:CustomerID>{invoice.customer_id or ""}</nsSAFT:CustomerID>
              <nsSAFT:Name>{self._escape_xml(invoice.customer.name or "")}</nsSAFT:Name>
    {self._build_invoice_customer_address(invoice)}
            </nsSAFT:CustomerInfo>
            <nsSAFT:AccountID>411</nsSAFT:AccountID>
            <nsSAFT:Period>{invoice.date.month}</nsSAFT:Period>
            <nsSAFT:PeriodYear>{invoice.date.year}</nsSAFT:PeriodYear>
            <nsSAFT:InvoiceDate>{self._format_date(invoice.date)}</nsSAFT:InvoiceDate>
            <nsSAFT:InvoiceType>{invoice.invoice_type or "01"}</nsSAFT:InvoiceType>
            <nsSAFT:SelfBillingIndicator>N</nsSAFT:SelfBillingIndicator>
            <nsSAFT:SourceID>{invoice.created_by_id or "system"}</nsSAFT:SourceID>
            <nsSAFT:GLPostingDate>{self._format_date(invoice.date_created or invoice.date)}</nsSAFT:GLPostingDate>
            <nsSAFT:TransactionID>{invoice.journal_entry_id or ""}</nsSAFT:TransactionID>
    {lines_xml}
            <nsSAFT:InvoiceDocumentTotals>
              <nsSAFT:TaxInformationTotals>
                <nsSAFT:TaxType>VAT</nsSAFT:TaxType>
                <nsSAFT:TaxCode>{invoice.vat_rate or "20"}</nsSAFT:TaxCode>
                <nsSAFT:TaxPercentage>{self._format_decimal(invoice.vat_rate or Decimal(20))}</nsSAFT:TaxPercentage>
                <nsSAFT:TaxBase>{self._format_decimal(invoice.subtotal)}</nsSAFT:TaxBase>
                <nsSAFT:TaxAmount>
                  <nsSAFT:Amount>{self._format_decimal(invoice.vat_amount)}</nsSAFT:Amount>
                  <nsSAFT:CurrencyCode>{invoice.currency or "BGN"}</nsSAFT:CurrencyCode>
                  <nsSAFT:CurrencyAmount>{self._format_decimal(invoice.vat_amount)}</nsSAFT:CurrencyAmount>
                  <nsSAFT:ExchangeRate>1.00</nsSAFT:ExchangeRate>
                </nsSAFT:TaxAmount>
              </nsSAFT:TaxInformationTotals>
              <nsSAFT:NetTotal>{self._format_decimal(invoice.subtotal)}</nsSAFT:NetTotal>
              <nsSAFT:GrossTotal>{self._format_decimal(invoice.total)}</nsSAFT:GrossTotal>
            </nsSAFT:InvoiceDocumentTotals>
          </nsSAFT:Invoice>
        """

    def _build_invoice_customer_address(self, invoice: Any) -> str:
        return f"""
              <nsSAFT:BillingAddress>
                <nsSAFT:StreetName>{self._escape_xml(invoice.customer.address or "")}</nsSAFT:StreetName>
                <nsSAFT:City>{self._escape_xml(invoice.customer.city or "")}</nsSAFT:City>
                <nsSAFT:PostalCode>{invoice.customer.postal_code or ""}</nsSAFT:PostalCode>
                <nsSAFT:Country>{invoice.customer.country or "BG"}</nsSAFT:Country>
              </nsSAFT:BillingAddress>
        """

    def _build_invoice_line(self, line: Any, index: int) -> str:
        return f"""
            <nsSAFT:InvoiceLine>
              <nsSAFT:LineNumber>{index}</nsSAFT:LineNumber>
              <nsSAFT:AccountID>{line.account_code or "411"}</nsSAFT:AccountID>
              <nsSAFT:ProductCode>{line.product.code or ""}</nsSAFT:ProductCode>
              <nsSAFT:ProductDescription>{self._escape_xml(line.description or line.product.name or "")}</nsSAFT:ProductDescription>
              <nsSAFT:Quantity>{self._format_decimal(line.quantity)}</nsSAFT:Quantity>
              <nsSAFT:InvoiceUOM>{line.unit or "PCE"}</nsSAFT:InvoiceUOM>
              <nsSAFT:UnitPrice>{self._format_decimal(line.unit_price)}</nsSAFT:UnitPrice>
              <nsSAFT:TaxPointDate>{self._format_date(line.date or date.today())}</nsSAFT:TaxPointDate>
              <nsSAFT:Description>{self._escape_xml(line.description or "")}</nsSAFT:Description>
              <nsSAFT:InvoiceLineAmount>
                <nsSAFT:Amount>{self._format_decimal(line.amount)}</nsSAFT:Amount>
                <nsSAFT:CurrencyCode>{line.currency or "BGN"}</nsSAFT:CurrencyCode>
                <nsSAFT:CurrencyAmount>{self._format_decimal(line.amount)}</nsSAFT:CurrencyAmount>
                <nsSAFT:ExchangeRate>1.00</nsSAFT:ExchangeRate>
              </nsSAFT:InvoiceLineAmount>
              <nsSAFT:DebitCreditIndicator>C</nsSAFT:DebitCreditIndicator>
              <nsSAFT:TaxInformation>
                <nsSAFT:TaxType>VAT</nsSAFT:TaxType>
                <nsSAFT:TaxCode>{line.vat_rate or "20"}</nsSAFT:TaxCode>
                <nsSAFT:TaxPercentage>{self._format_decimal(line.vat_rate or Decimal(20))}</nsSAFT:TaxPercentage>
                <nsSAFT:TaxBase>{self._format_decimal(line.amount)}</nsSAFT:TaxBase>
                <nsSAFT:TaxAmount>
                  <nsSAFT:Amount>{self._format_decimal(line.vat_amount or Decimal(0))}</nsSAFT:Amount>
                  <nsSAFT:CurrencyCode>{line.currency or "BGN"}</nsSAFT:CurrencyCode>
                  <nsSAFT:CurrencyAmount>{self._format_decimal(line.vat_amount or Decimal(0))}</nsSAFT:CurrencyAmount>
                  <nsSAFT:ExchangeRate>1.00</nsSAFT:ExchangeRate>
                </nsSAFT:TaxAmount>
              </nsSAFT:TaxInformation>
            </nsSAFT:InvoiceLine>
        """

    def _build_purchase_invoices(self) -> str:
        invoices = self._get_purchase_invoices()
        total_debit, total_credit = self._calculate_invoice_totals(invoices)
        invoices_xml = "\n".join([self._build_purchase_invoice(invoice) for invoice in invoices])
        if not invoices:
            invoices_xml = self._build_placeholder_purchase_invoice()
        return f"""
      <nsSAFT:PurchaseInvoices>
        <nsSAFT:NumberOfEntries>{len(invoices)}</nsSAFT:NumberOfEntries>
        <nsSAFT:TotalDebit>{self._format_decimal(total_debit)}</nsSAFT:TotalDebit>
        <nsSAFT:TotalCredit>{self._format_decimal(total_credit)}</nsSAFT:TotalCredit>
  {invoices_xml}
      </nsSAFT:PurchaseInvoices>
        """

    def _build_placeholder_purchase_invoice(self) -> str:
        return ""

    def _build_purchase_invoice(self, invoice: Any) -> str:
        return ""

    def _build_payments(self) -> str:
        payments = self._get_payments()
        total_amount = sum(p.amount for p in payments)
        payments_xml = "\n".join([self._build_payment(payment) for payment in payments])
        if not payments:
            payments_xml = self._build_placeholder_payment()

        return f"""
      <nsSAFT:Payments>
        <nsSAFT:NumberOfEntries>{len(payments)}</nsSAFT:NumberOfEntries>
        <nsSAFT:TotalDebit>{self._format_decimal(total_amount)}</nsSAFT:TotalDebit>
        <nsSAFT:TotalCredit>{self._format_decimal(total_amount)}</nsSAFT:TotalCredit>
  {payments_xml}
      </nsSAFT:Payments>
        """

    def _build_placeholder_payment(self) -> str:
        return ""

    def _build_payment(self, payment: Any) -> str:
        return ""

    def _build_movement_of_goods(self, **kwargs: Any) -> str:
        movements = self._get_stock_movements(**kwargs)
        if not movements:
            return ""

        movements_xml = "\n".join([self._build_stock_movement(movement) for movement in movements])
        return f"""
        <nsSAFT:MovementOfGoods>
          <nsSAFT:NumberOfMovementLines>{len(movements)}</nsSAFT:NumberOfMovementLines>
          <nsSAFT:TotalQuantityIssued>{self._calculate_quantity_issued(movements)}</nsSAFT:TotalQuantityIssued>
          <nsSAFT:TotalQuantityReceived>{self._calculate_quantity_received(movements)}</nsSAFT:TotalQuantityReceived>
    {movements_xml}
        </nsSAFT:MovementOfGoods>
        """

    def _build_stock_movement(self, movement: Any) -> str:
        return ""

    def _build_movement_lines(self, lines: List[Any]) -> str:
        return ""

    def _build_movement_line(self, line: Any, index: int) -> str:
        return ""

    def _calculate_quantity_issued(self, movements: List[Any]) -> str:
        return "0.00"

    def _calculate_quantity_received(self, movements: List[Any]) -> str:
        return "0.00"

    def _build_asset_transactions(self) -> str:
        transactions = self._get_asset_transactions()
        if not transactions:
            return ""

        transactions_xml = "\n".join([self._build_asset_transaction(t) for t in transactions])
        return f"""
        <nsSAFT:AssetTransactions>
          <nsSAFT:NumberOfAssetTransactions>{len(transactions)}</nsSAFT:NumberOfAssetTransactions>
    {transactions_xml}
        </nsSAFT:AssetTransactions>
        """

    def _build_asset_transaction(self, transaction: Any) -> str:
        transaction_type = AssetMovementType.from_internal_type(transaction.transaction_type)
        return f"""
          <nsSAFT:AssetTransaction>
            <nsSAFT:AssetTransactionID>{transaction.id}</nsSAFT:AssetTransactionID>
            <nsSAFT:AssetID>{transaction.asset.code}</nsSAFT:AssetID>
            <nsSAFT:AssetTransactionType>{transaction_type}</nsSAFT:AssetTransactionType>
            <nsSAFT:Description>{self._escape_xml(transaction.description or AssetMovementType.name_bg(transaction_type))}</nsSAFT:Description>
            <nsSAFT:AssetTransactionDate>{self._format_date(transaction.transaction_date)}</nsSAFT:AssetTransactionDate>
    {self._build_asset_supplier_customer(transaction)}
            <nsSAFT:TransactionID>{transaction.journal_entry_id or ""}</nsSAFT:TransactionID>
            <nsSAFT:AssetTransactionValuations>
              <nsSAFT:AssetTransactionValuation>
                <nsSAFT:AcquisitionAndProductionCostsOnTransaction>{self._format_decimal(transaction.acquisition_cost or Decimal(0))}</nsSAFT:AcquisitionAndProductionCostsOnTransaction>
                <nsSAFT:BookValueOnTransaction>{self._format_decimal(transaction.book_value or Decimal(0))}</nsSAFT:BookValueOnTransaction>
                <nsSAFT:AssetTransactionAmount>{self._format_decimal(transaction.amount)}</nsSAFT:AssetTransactionAmount>
              </nsSAFT:AssetTransactionValuation>
            </nsSAFT:AssetTransactionValuations>
          </nsSAFT:AssetTransaction>
        """

    def _build_asset_supplier_customer(self, transaction: Any) -> str:
        if not (transaction.supplier_name or transaction.customer_name):
            return ""
        name = transaction.supplier_name or transaction.customer_name
        id = transaction.supplier_id or transaction.customer_id or ""
        return f"""
            <nsSAFT:AssetSupplierCustomer>
              <nsSAFT:SupplierCustomerName>{self._escape_xml(name)}</nsSAFT:SupplierCustomerName>
              <nsSAFT:SupplierCustomerID>{id}</nsSAFT:SupplierCustomerID>
              <nsSAFT:PostalAddress>
                <nsSAFT:City>{self._escape_xml(transaction.city or "")}</nsSAFT:City>
                <nsSAFT:Country>{transaction.country or "BG"}</nsSAFT:Country>
              </nsSAFT:PostalAddress>
            </nsSAFT:AssetSupplierCustomer>
        """

    def _calculate_invoice_totals(self, invoices: List[Any]) -> Tuple[Decimal, Decimal]:
        total_debit = Decimal(0)
        total_credit = Decimal(0)
        for invoice in invoices:
            total = invoice.total or Decimal(0)
            total_debit += total
            total_credit += total
        return total_debit, total_credit

    def _escape_xml(self, text: Optional[str]) -> str:
        if not text:
            return ""
        return html.escape(text)

    def _format_decimal(self, value: Optional[Decimal]) -> str:
        if value is None:
            return "0.00"
        return str(value.quantize(Decimal("0.01")))

    def _format_date(self, value: Optional[date]) -> str:
        if value is None:
            return date.today().isoformat()
        return value.isoformat()

    def _get_sales_invoices(self) -> List[Any]:
        with Session(self.organization.engine) as session:
            start_date = date(self.year, self.month, 1)
            end_date = date(self.year, self.month, 1).replace(day=28) + timedelta(days=4)
            end_date = end_date - timedelta(days=end_date.day)

            statement = (
                select(Sale)
                .options(selectinload(Sale.lines), selectinload(Sale.customer))
                .where(Sale.organization_id == self.organization.id)
                .where(Sale.date >= start_date)
                .where(Sale.date <= end_date)
                .order_by(Sale.date, Sale.id)
            )
            sales = session.exec(statement).all()
            return sales

    def _get_purchase_invoices(self) -> List[Any]:
        with Session(self.organization.engine) as session:
            start_date = date(self.year, self.month, 1)
            end_date = date(self.year, self.month, 1).replace(day=28) + timedelta(days=4)
            end_date = end_date - timedelta(days=end_date.day)

            statement = (
                select(Purchase)
                .options(selectinload(Purchase.lines), selectinload(Purchase.supplier))
                .where(Purchase.organization_id == self.organization.id)
                .where(Purchase.date >= start_date)
                .where(Purchase.date <= end_date)
                .order_by(Purchase.date, Purchase.id)
            )
            purchases = session.exec(statement).all()
            return purchases

    def _get_payments(self) -> List[Any]:
        with Session(self.organization.engine) as session:
            start_date = date(self.year, self.month, 1)
            end_date = date(self.year, self.month, 1).replace(day=28) + timedelta(days=4)
            end_date = end_date - timedelta(days=end_date.day)

            statement = (
                select(Payment)
                .where(Payment.organization_id == self.organization.id)
                .where(Payment.date_payment >= start_date)
                .where(Payment.date_payment <= end_date)
                .order_by(Payment.date_payment, Payment.id)
            )
            payments = session.exec(statement).all()
            return payments

    def _get_stock_movements(self, start_date: date, end_date: date) -> List[Any]:
        with Session(self.organization.engine) as session:
            statement = (
                select(StockMovement)
                .where(StockMovement.organization_id == self.organization.id)
                .where(StockMovement.date >= start_date)
                .where(StockMovement.date <= end_date)
                .order_by(StockMovement.date, StockMovement.id)
            )
            movements = session.exec(statement).all()
            return movements

    def _get_asset_transactions(self) -> List[Any]:
        with Session(self.organization.engine) as session:
            start_date = date(self.year, 1, 1)
            end_date = date(self.year, 12, 31)

            statement = (
                select(AssetTransaction)
                .where(AssetTransaction.organization_id == self.organization.id)
                .where(AssetTransaction.transaction_date >= start_date)
                .where(AssetTransaction.transaction_date <= end_date)
                .order_by(AssetTransaction.transaction_date, AssetTransaction.id)
            )
            transactions = session.exec(statement).all()
            return transactions