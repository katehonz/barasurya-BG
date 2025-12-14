
import html
from datetime import date, timedelta
from decimal import Decimal
from typing import IO, Any, List, Optional, Tuple

from sqlalchemy.orm import selectinload
from sqlmodel import Session, select

from app.models.entry_line import EntryLine
from app.models.journal_entry import JournalEntry
from app.models.organization import Organization


class SAFTGeneralLedgerEntries:
    def __init__(self, organization: Organization, year: int, month: Optional[int] = None):
        self.organization = organization
        self.year = year
        self.month = month

    def generate(self, output: IO[Any], **kwargs: Any):
        entries = self._get_journal_entries()
        total_debit, total_credit = self._calculate_totals(entries)
        number_of_entries = len(entries)

        entries_xml = "\n".join([self._build_journal_entry(entry) for entry in entries])
        journal_placeholder = self._build_journal_placeholder() if not entries else entries_xml

        content = f"""
      <nsSAFT:GeneralLedgerEntries>
        <nsSAFT:NumberOfEntries>{number_of_entries}</nsSAFT:NumberOfEntries>
        <nsSAFT:TotalDebit>{self._format_decimal(total_debit)}</nsSAFT:TotalDebit>
        <nsSAFT:TotalCredit>{self._format_decimal(total_credit)}</nsSAFT:TotalCredit>
    {journal_placeholder}
      </nsSAFT:GeneralLedgerEntries>
        """
        output.write(content)

    def _get_journal_entries(self) -> List[Any]:
        with Session(self.organization.engine) as session:
            start_date = date(self.year, self.month, 1)
            end_date = date(self.year, self.month, 1).replace(day=28) + timedelta(days=4)
            end_date = end_date - timedelta(days=end_date.day)

            statement = (
                select(JournalEntry)
                .options(selectinload(JournalEntry.lines).selectinload(EntryLine.account))
                .where(JournalEntry.organization_id == self.organization.id)
                .where(JournalEntry.is_posted == True)
                .where(JournalEntry.date >= start_date)
                .where(JournalEntry.date <= end_date)
                .order_by(JournalEntry.date, JournalEntry.id, EntryLine.id)
            )
            entries = session.exec(statement).all()
            return entries

    def _calculate_totals(self, entries: List[Any]) -> Tuple[Decimal, Decimal]:
        total_debit = Decimal(0)
        total_credit = Decimal(0)
        for entry in entries:
            for line in entry.lines:
                total_debit += Decimal(line.debit)
                total_credit += Decimal(line.credit)
        return total_debit, total_credit

    def _build_journal_placeholder(self) -> str:
        today = date.today().isoformat()
        first_day_of_month = date(self.year, self.month, 1).isoformat()
        return f"""
            <nsSAFT:Journal>
              <nsSAFT:JournalID>GJ</nsSAFT:JournalID>
              <nsSAFT:Description>Главен журнал</nsSAFT:Description>
              <nsSAFT:Type>GJ</nsSAFT:Type>
              <nsSAFT:Transaction>
                <nsSAFT:TransactionID>0</nsSAFT:TransactionID>
                <nsSAFT:Period>{self.month}</nsSAFT:Period>
                <nsSAFT:PeriodYear>{self.year}</nsSAFT:PeriodYear>
                <nsSAFT:TransactionDate>{first_day_of_month}</nsSAFT:TransactionDate>
                <nsSAFT:Description>Няма записи за периода</nsSAFT:Description>
                <nsSAFT:SystemEntryDate>{today}</nsSAFT:SystemEntryDate>
                <nsSAFT:GLPostingDate>{first_day_of_month}</nsSAFT:GLPostingDate>
                <nsSAFT:CustomerID></nsSAFT:CustomerID>
                <nsSAFT:SupplierID></nsSAFT:SupplierID>
                <nsSAFT:TransactionLine>
                  <nsSAFT:RecordID>0</nsSAFT:RecordID>
                  <nsSAFT:AccountID>100</nsSAFT:AccountID>
                  <nsSAFT:TaxpayerAccountID>100</nsSAFT:TaxpayerAccountID>
                  <nsSAFT:CustomerID></nsSAFT:CustomerID>
                  <nsSAFT:SupplierID></nsSAFT:SupplierID>
                  <nsSAFT:Description>Няма записи</nsSAFT:Description>
                  <nsSAFT:DebitAmount>
                    <nsSAFT:Amount>0.00</nsSAFT:Amount>
                    <nsSAFT:CurrencyCode>BGN</nsSAFT:CurrencyCode>
                    <nsSAFT:CurrencyAmount>0.00</nsSAFT:CurrencyAmount>
                    <nsSAFT:ExchangeRate>1.00</nsSAFT:ExchangeRate>
                  </nsSAFT:DebitAmount>
                  <nsSAFT:TaxInformation>
                    <nsSAFT:TaxType>VAT</nsSAFT:TaxType>
                    <nsSAFT:TaxCode>0</nsSAFT:TaxCode>
                    <nsSAFT:TaxPercentage>0.00</nsSAFT:TaxPercentage>
                    <nsSAFT:TaxBase>0.00</nsSAFT:TaxBase>
                    <nsSAFT:TaxAmount>
                      <nsSAFT:Amount>0.00</nsSAFT:Amount>
                      <nsSAFT:CurrencyCode>BGN</nsSAFT:CurrencyCode>
                      <nsSAFT:CurrencyAmount>0.00</nsSAFT:CurrencyAmount>
                      <nsSAFT:ExchangeRate>1.00</nsSAFT:ExchangeRate>
                    </nsSAFT:TaxAmount>
                  </nsSAFT:TaxInformation>
                </nsSAFT:TransactionLine>
              </nsSAFT:Transaction>
            </nsSAFT:Journal>
        """

    def _build_journal_entry(self, entry: Any) -> str:
        lines_xml = "\n".join([self._build_line(line) for line in entry.lines])
        return f"""
          <nsSAFT:Journal>
            <nsSAFT:JournalID>{entry.journal_type or "GJ"}</nsSAFT:JournalID>
            <nsSAFT:Description>{self._escape_xml(entry.journal_description or "Главен журнал")}</nsSAFT:Description>
            <nsSAFT:Type>{entry.journal_type or "GJ"}</nsSAFT:Type>
            <nsSAFT:Transaction>
              <nsSAFT:TransactionID>{entry.id}</nsSAFT:TransactionID>
              <nsSAFT:Period>{entry.period or entry.date.month}</nsSAFT:Period>
              <nsSAFT:PeriodYear>{entry.period_year or entry.date.year}</nsSAFT:PeriodYear>
              <nsSAFT:TransactionDate>{self._format_date(entry.date)}</nsSAFT:TransactionDate>
              <nsSAFT:SourceID>{entry.created_by or "system"}</nsSAFT:SourceID>
              <nsSAFT:TransactionType>{entry.transaction_type or "N"}</nsSAFT:TransactionType>
              <nsSAFT:Description>{self._escape_xml(entry.description or "")}</nsSAFT:Description>
              <nsSAFT:SystemEntryDate>{self._format_date(entry.inserted_at)}</nsSAFT:SystemEntryDate>
              <nsSAFT:GLPostingDate>{self._format_date(entry.posted_at or entry.date)}</nsSAFT:GLPostingDate>
    {lines_xml}
            </nsSAFT:Transaction>
          </nsSAFT:Journal>
        """

    def _build_line(self, line: Any) -> str:
        is_debit = (line.debit or Decimal(0)) > 0
        return f"""
              <nsSAFT:TransactionLine>
                <nsSAFT:RecordID>{line.id}</nsSAFT:RecordID>
                <nsSAFT:AccountID>{line.account_code}</nsSAFT:AccountID>
                <nsSAFT:SourceDocumentID>{line.source_document_id or ""}</nsSAFT:SourceDocumentID>
    {self._build_customer_supplier_id(line)}
                <nsSAFT:Description>{self._escape_xml(line.description or "")}</nsSAFT:Description>
    {self._build_debit_amount(line) if is_debit else self._build_credit_amount(line)}
    {self._build_tax_information(line)}
              </nsSAFT:TransactionLine>
        """

    def _build_customer_supplier_id(self, line: Any) -> str:
        if line.customer_id:
            return f"            <nsSAFT:CustomerID>{line.customer_id}</nsSAFT:CustomerID>"
        if line.supplier_id:
            return f"            <nsSAFT:SupplierID>{line.supplier_id}</nsSAFT:SupplierID>"
        return ""

    def _build_debit_amount(self, line: Any) -> str:
        amount = line.debit or Decimal(0)
        return f"""
                <nsSAFT:DebitAmount>
                  <nsSAFT:Amount>{self._format_decimal(amount)}</nsSAFT:Amount>
                  <nsSAFT:CurrencyCode>{line.currency or "BGN"}</nsSAFT:CurrencyCode>
                  <nsSAFT:CurrencyAmount>{self._format_decimal(line.currency_amount or amount)}</nsSAFT:CurrencyAmount>
                  <nsSAFT:ExchangeRate>{self._format_decimal(line.exchange_rate or Decimal(1))}</nsSAFT:ExchangeRate>
                </nsSAFT:DebitAmount>
        """

    def _build_credit_amount(self, line: Any) -> str:
        amount = line.credit or Decimal(0)
        return f"""
                <nsSAFT:CreditAmount>
                  <nsSAFT:Amount>{self._format_decimal(amount)}</nsSAFT:Amount>
                  <nsSAFT:CurrencyCode>{line.currency or "BGN"}</nsSAFT:CurrencyCode>
                  <nsSAFT:CurrencyAmount>{self._format_decimal(line.currency_amount or amount)}</nsSAFT:CurrencyAmount>
                  <nsSAFT:ExchangeRate>{self._format_decimal(line.exchange_rate or Decimal(1))}</nsSAFT:ExchangeRate>
                </nsSAFT:CreditAmount>
        """

    def _build_tax_information(self, line: Any) -> str:
        if line.vat_amount and line.vat_amount > 0:
            return f"""
                <nsSAFT:TaxInformation>
                  <nsSAFT:TaxType>VAT</nsSAFT:TaxType>
                  <nsSAFT:TaxCode>{line.vat_rate or "20"}</nsSAFT:TaxCode>
                  <nsSAFT:TaxPercentage>{self._format_decimal(line.vat_rate or Decimal(20))}</nsSAFT:TaxPercentage>
                  <nsSAFT:TaxBase>{self._format_decimal(line.tax_base or line.debit or line.credit)}</nsSAFT:TaxBase>
                  <nsSAFT:TaxAmount>
                    <nsSAFT:Amount>{self._format_decimal(line.vat_amount)}</nsSAFT:Amount>
                    <nsSAFT:CurrencyCode>{line.currency or "BGN"}</nsSAFT:CurrencyCode>
                    <nsSAFT:CurrencyAmount>{self._format_decimal(line.vat_amount)}</nsSAFT:CurrencyAmount>
                    <nsSAFT:ExchangeRate>{self._format_decimal(line.exchange_rate or Decimal(1))}</nsSAFT:ExchangeRate>
                  </nsSAFT:TaxAmount>
                </nsSAFT:TaxInformation>
            """
        return ""

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
