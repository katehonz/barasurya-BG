

import html
from datetime import date, timedelta
from decimal import Decimal
from typing import IO, Any, List, Optional, Tuple
from uuid import UUID

from sqlalchemy.orm import selectinload
from sqlmodel import Session, func, select

from app.models.account import Account
from app.models.asset import Asset
from app.models.contraagent import Contraagent # Changed from Customer
from app.models.entry_line import EntryLine
from app.models.journal_entry import JournalEntry
from app.models.organization import Organization
from app.models.product import Product # Changed from Item
# Removed from app.models.supplier import Supplier


class SAFTMasterFiles:
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
      <nsSAFT:MasterFilesMonthly>
    {self._build_general_ledger_accounts()}
    {self._build_customers()}
    {self._build_suppliers()}
    {self._build_tax_table()}
    {self._build_uom_table()}
    {self._build_products()}
      </nsSAFT:MasterFilesMonthly>
        """

    def _build_annual(self) -> str:
        return f"""
      <nsSAFT:MasterFilesAnnual>
    {self._build_assets()}
      </nsSAFT:MasterFilesAnnual>
        """

    def _build_on_demand(self, **kwargs: Any) -> str:
        return f"""
      <nsSAFT:MasterFilesOnDemand>
    {self._build_products()}
    {self._build_physical_stock(**kwargs)}
      </nsSAFT:MasterFilesOnDemand>
        """

    def _build_general_ledger_accounts(self) -> str:
        accounts = self._get_accounts_with_balances()
        accounts_xml = "\n".join([self._build_account(account) for account in accounts])
        return f"""
      <nsSAFT:GeneralLedgerAccounts>
  {accounts_xml}
      </nsSAFT:GeneralLedgerAccounts>
        """

    def _build_account(self, account_data: Any) -> str:
        account = account_data["account"]
        opening_balance = account_data["opening_balance"]
        closing_balance = account_data["closing_balance"]

        opening_debit = "0.00"
        opening_credit = "0.00"
        closing_debit = "0.00"
        closing_credit = "0.00"

        if account.is_debit_account:
            if opening_balance >= 0:
                opening_debit = self._format_decimal(opening_balance)
            else:
                opening_credit = self._format_decimal(-opening_balance)
            if closing_balance >= 0:
                closing_debit = self._format_decimal(closing_balance)
            else:
                closing_credit = self._format_decimal(-closing_balance)
        else:  # credit account
            if opening_balance >= 0:
                opening_credit = self._format_decimal(opening_balance)
            else:
                opening_debit = self._format_decimal(-opening_balance)
            if closing_balance >= 0:
                closing_credit = self._format_decimal(closing_balance)
            else:
                closing_debit = self._format_decimal(-closing_balance)

        # This logic for account type is a simplification.
        account_type = "Bifunctional" # Safest default for SAF-T

        return f"""
          <nsSAFT:Account>
            <nsSAFT:AccountID>{account.code}</nsSAFT:AccountID>
            <nsSAFT:AccountDescription>{self._escape_xml(account.name)}</nsSAFT:AccountDescription>
            <nsSAFT:TaxpayerAccountID>{getattr(account, 'standard_code', account.code)}</nsSAFT:TaxpayerAccountID>
            <nsSAFT:AccountType>{account_type}</nsSAFT:AccountType>
            <nsSAFT:AccountCreationDate>{self._format_date(getattr(account, 'inserted_at', account.date_created))}</nsSAFT:AccountCreationDate>
            <nsSAFT:OpeningDebitBalance>{opening_debit}</nsSAFT:OpeningDebitBalance>
            <nsSAFT:OpeningCreditBalance>{opening_credit}</nsSAFT:OpeningCreditBalance>
            <nsSAFT:ClosingDebitBalance>{closing_debit}</nsSAFT:ClosingDebitBalance>
            <nsSAFT:ClosingCreditBalance>{closing_credit}</nsSAFT:ClosingCreditBalance>
          </nsSAFT:Account>
        """

    def _build_customers(self) -> str:
        contraagents = self._get_contraagents(is_customer=True)
        contraagents_xml = "\n".join([self._build_contraagent_customer(ca) for ca in contraagents])
        return f"""
      <nsSAFT:Customers>
  {contraagents_xml}
      </nsSAFT:Customers>
        """

    def _build_contraagent_customer(self, contraagent: Contraagent) -> str:
        # Contraagent fields for SAF-T Customer
        opening_balance = contraagent.opening_debit_balance or Decimal(0)
        closing_balance = contraagent.closing_debit_balance or Decimal(0)
        return f"""
          <nsSAFT:Customer>
    {self._build_company_structure(contraagent)}
            <nsSAFT:CustomerID>{contraagent.registration_number or contraagent.id}</nsSAFT:CustomerID>
            <nsSAFT:SelfBillingIndicator>{"Y" if contraagent.self_billing_indicator else "N"}</nsSAFT:SelfBillingIndicator>
            <nsSAFT:AccountID>411</nsSAFT:AccountID>
            <nsSAFT:OpeningDebitBalance>{self._format_decimal(opening_balance)}</nsSAFT:OpeningDebitBalance>
            <nsSAFT:ClosingDebitBalance>{self._format_decimal(closing_balance)}</nsSAFT:ClosingDebitBalance>
          </nsSAFT:Customer>
        """

    def _build_suppliers(self) -> str:
        contraagents = self._get_contraagents(is_supplier=True)
        contraagents_xml = "\n".join([self._build_contraagent_supplier(ca) for ca in contraagents])
        return f"""
      <nsSAFT:Suppliers>
  {contraagents_xml}
      </nsSAFT:Suppliers>
        """

    def _build_contraagent_supplier(self, contraagent: Contraagent) -> str:
        # Contraagent fields for SAF-T Supplier
        opening_balance = contraagent.opening_credit_balance or Decimal(0)
        closing_balance = contraagent.closing_credit_balance or Decimal(0)
        return f"""
          <nsSAFT:Supplier>
    {self._build_company_structure(contraagent)}
            <nsSAFT:SupplierID>{contraagent.registration_number or contraagent.id}</nsSAFT:SupplierID>
            <nsSAFT:SelfBillingIndicator>{"Y" if contraagent.self_billing_indicator else "N"}</nsSAFT:SelfBillingIndicator>
            <nsSAFT:AccountID>401</nsSAFT:AccountID>
            <nsSAFT:OpeningCreditBalance>{self._format_decimal(opening_balance)}</nsSAFT:OpeningCreditBalance>
            <nsSAFT:ClosingCreditBalance>{self._format_decimal(closing_balance)}</nsSAFT:ClosingCreditBalance>
          </nsSAFT:Supplier>
        """

    def _build_company_structure(self, contact: Any) -> str:
        city = contact.city or "София"
        country = contact.country or "BG"
        street = contact.street_name or ""
        postal_code = contact.postal_code or ""
        building_number = contact.building_number or ""
        related_party = "Y" if contact.related_party else "N"
        eik = contact.registration_number or ""
        vat_number = contact.vat_number or ""

        tax_registration = ""
        if eik or vat_number:
            tax_type = "100010" if vat_number else "100020"
            tax_registration = f"""
              <nsSAFT:TaxRegistration>
                <nsSAFT:TaxRegistrationNumber>{self._format_eik(eik)}</nsSAFT:TaxRegistrationNumber>
                <nsSAFT:TaxType>{tax_type}</nsSAFT:TaxType>
                <nsSAFT:TaxNumber>{vat_number}</nsSAFT:TaxNumber>
              </nsSAFT:TaxRegistration>
            """

        bank_account = ""
        if contact.iban_number:
            bank_account = f"""
              <nsSAFT:BankAccount>
                <nsSAFT:IBANNumber>{contact.iban_number}</nsSAFT:IBANNumber>
              </nsSAFT:BankAccount>
            """

        return f"""
            <nsSAFT:CompanyStructure>
              <nsSAFT:RegistrationNumber>{self._format_eik(eik)}</nsSAFT:RegistrationNumber>
              <nsSAFT:Name>{self._escape_xml(contact.name)}</nsSAFT:Name>
              <nsSAFT:Address>
                <nsSAFT:StreetName>{self._escape_xml(street)}</nsSAFT:StreetName>
                <nsSAFT:Number>{building_number}</nsSAFT:Number>
                <nsSAFT:City>{self._escape_xml(city)}</nsSAFT:City>
                <nsSAFT:PostalCode>{postal_code}</nsSAFT:PostalCode>
                <nsSAFT:Country>{country}</nsSAFT:Country>
                <nsSAFT:AddressType>StreetAddress</nsSAFT:AddressType>
              </nsSAFT:Address>
    {tax_registration}{bank_account}          <nsSAFT:RelatedParty>{related_party}</nsSAFT:RelatedParty>
            </nsSAFT:CompanyStructure>
        """

    def _build_tax_table(self) -> str:
        return """
        <nsSAFT:TaxTable>
          <nsSAFT:TaxTableEntry>
            <nsSAFT:TaxType>VAT</nsSAFT:TaxType>
            <nsSAFT:Description>ДДС 20%</nsSAFT:Description>
            <nsSAFT:TaxCodeDetails>
              <nsSAFT:TaxCode>20</nsSAFT:TaxCode>
              <nsSAFT:Description>Стандартна ставка</nsSAFT:Description>
              <nsSAFT:TaxPercentage>20.00</nsSAFT:TaxPercentage>
              <nsSAFT:Country>BG</nsSAFT:Country>
            </nsSAFT:TaxCodeDetails>
          </nsSAFT:TaxTableEntry>
          <nsSAFT:TaxTableEntry>
            <nsSAFT:TaxType>VAT</nsSAFT:TaxType>
            <nsSAFT:Description>ДДС 9%</nsSAFT:Description>
            <nsSAFT:TaxCodeDetails>
              <nsSAFT:TaxCode>9</nsSAFT:TaxCode>
              <nsSAFT:Description>Намалена ставка</nsSAFT:Description>
              <nsSAFT:TaxPercentage>9.00</nsSAFT:TaxPercentage>
              <nsSAFT:Country>BG</nsSAFT:Country>
            </nsSAFT:TaxCodeDetails>
          </nsSAFT:TaxTableEntry>
          <nsSAFT:TaxTableEntry>
            <nsSAFT:TaxType>VAT</nsSAFT:TaxType>
            <nsSAFT:Description>ДДС 0%</nsSAFT:Description>
            <nsSAFT:TaxCodeDetails>
              <nsSAFT:TaxCode>0</nsSAFT:TaxCode>
              <nsSAFT:Description>Нулева ставка</nsSAFT:Description>
              <nsSAFT:TaxPercentage>0.00</nsSAFT:TaxPercentage>
              <nsSAFT:Country>BG</nsSAFT:Country>
            </nsSAFT:TaxCodeDetails>
          </nsSAFT:TaxTableEntry>
        </nsSAFT:TaxTable>
        """

    def _build_uom_table(self) -> str:
        return """
    <nsSAFT:UOMTable>
        <nsSAFT:UOMTableEntry>
            <nsSAFT:UnitOfMeasure>PCE</nsSAFT:UnitOfMeasure>
            <nsSAFT:Description>Брой</nsSAFT:Description>
        </nsSAFT:UOMTableEntry>
        <nsSAFT:UOMTableEntry>
            <nsSAFT:UnitOfMeasure>KGM</nsSAFT:UnitOfMeasure>
            <nsSAFT:Description>Килограм</nsSAFT:Description>
        </nsSAFT:UOMTableEntry>
        <nsSAFT:UOMTableEntry>
            <nsSAFT:UnitOfMeasure>MTR</nsSAFT:UnitOfMeasure>
            <nsSAFT:Description>Метър</nsSAFT:Description>
        </nsSAFT:UOMTableEntry>
        <nsSAFT:UOMTableEntry>
            <nsSAFT:UnitOfMeasure>LTR</nsSAFT:UnitOfMeasure>
            <nsSAFT:Description>Литър</nsSAFT:Description>
        </nsSAFT:UOMTableEntry>
    </nsSAFT:UOMTable>
        """

    def _build_products(self) -> str:
        products = self._get_products()
        products_xml = "\n".join([self._build_product(product) for product in products])
        return f"""
      <nsSAFT:Products>
  {products_xml}
      </nsSAFT:Products>
        """

    def _build_product(self, product: Product) -> str:
        # TODO: Get cn_code and goods_services_id from product model
        cn_code = ""
        goods_services_id = "G" # Default to Goods
        
        return f"""
          <nsSAFT:Product>
            <nsSAFT:ProductCode>{product.id}</nsSAFT:ProductCode>
            <nsSAFT:GoodsServicesID>{goods_services_id}</nsSAFT:GoodsServicesID>
            <nsSAFT:ProductGroup>{self._escape_xml(product.name)}</nsSAFT:ProductGroup>
            <nsSAFT:Description>{self._escape_xml(product.name)}</nsSAFT:Description>
            <nsSAFT:ProductCommodityCode>{cn_code}</nsSAFT:ProductCommodityCode>
            <nsSAFT:UOMBase>PCE</nsSAFT:UOMBase>
            <nsSAFT:UOMStandard>PCE</nsSAFT:UOMStandard>
            <nsSAFT:UOMToUOMBaseConversionFactor>1.00</nsSAFT:UOMToUOMBaseConversionFactor>
          </nsSAFT:Product>
        """

    def _build_physical_stock(self, **kwargs: Any) -> str:
        # TODO: Get physical stock
        stock_items = []
        if not stock_items:
            return ""
        stock_xml = "\n".join([self._build_stock_item(item) for item in stock_items])
        return f"""
        <nsSAFT:PhysicalStock>
    {stock_xml}
        </nsSAFT:PhysicalStock>
        """

    def _build_stock_item(self, item: Any) -> str:
        return f"""
          <nsSAFT:PhysicalStockEntry>
            <nsSAFT:WarehouseID>{item.warehouse_id}</nsSAFT:WarehouseID>
            <nsSAFT:ProductCode>{item.product_code}</nsSAFT:ProductCode>
            <nsSAFT:StockAccountID>{item.account_id or "302"}</nsSAFT:StockAccountID>
            <nsSAFT:Quantity>{self._format_decimal(item.quantity)}</nsSAFT:Quantity>
            <nsSAFT:UOMPhysicalStock>{item.unit or "PCE"}</nsSAFT:UOMPhysicalStock>
            <nsSAFT:UnitPrice>{self._format_decimal(item.unit_price)}</nsSAFT:UnitPrice>
            <nsSAFT:StockValue>{self._format_decimal(item.stock_value)}</nsSAFT:StockValue>
          </nsSAFT:PhysicalStockEntry>
        """

    def _build_assets(self) -> str:
        assets = self._get_assets()
        if not assets:
            return ""
        assets_xml = "\n".join([self._build_asset(asset) for asset in assets])
        return f"""
        <nsSAFT:Assets>
    {assets_xml}
        </nsSAFT:Assets>
        """

    def _build_asset(self, asset: Any) -> str:
        return f"""
          <nsSAFT:Asset>
            <nsSAFT:AssetID>{asset.code}</nsSAFT:AssetID>
            <nsSAFT:AccountID>{asset.account_code or "205"}</nsSAFT:AccountID>
            <nsSAFT:Description>{self._escape_xml(asset.name)}</nsSAFT:Description>
    {self._build_asset_contraagent(asset)}
            <nsSAFT:PurchaseOrderDate>{self._format_date(asset.purchase_order_date or asset.acquisition_date)}</nsSAFT:PurchaseOrderDate>
            <nsSAFT:DateOfAcquisition>{self._format_date(asset.acquisition_date)}</nsSAFT:DateOfAcquisition>
            <nsSAFT:StartUpDate>{self._format_date(asset.startup_date or asset.acquisition_date)}</nsSAFT:StartUpDate>
    {self._build_asset_valuations(asset)}
          </nsSAFT:Asset>
        """

    def _build_asset_contraagent(self, asset: Any) -> str:
        if not asset.contraagent:
            return ""
        return f"""
            <nsSAFT:AssetSupplier>
              <nsSAFT:SupplierName>{self._escape_xml(asset.contraagent.name)}</nsSAFT:SupplierName>
              <nsSAFT:SupplierID>{asset.contraagent.vat_number or asset.contraagent.registration_number or ""}</nsSAFT:SupplierID>
              <nsSAFT:PostalAddress>
                <nsSAFT:City>{self._escape_xml(asset.contraagent.city or "")}</nsSAFT:City>
                <nsSAFT:Country>{asset.contraagent.country or "BG"}</nsSAFT:Country>
              </nsSAFT:PostalAddress>
            </nsSAFT:AssetSupplier>
        """

    def _build_asset_valuations(self, asset: Any) -> str:
        # TODO: Calculate depreciation rates
        depreciation_rate = 20.0
        tax_depreciation_rate = 25.0
        return f"""
            <nsSAFT:Valuations>
              <nsSAFT:ValuationSAP>
                <nsSAFT:ValuationClass>{asset.account_code or "205"}</nsSAFT:ValuationClass>
                <nsSAFT:AcquisitionAndProductionCostsBegin>{self._format_decimal(asset.acquisition_cost_begin_year or asset.acquisition_cost)}</nsSAFT:AcquisitionAndProductionCostsBegin>
                <nsSAFT:AcquisitionAndProductionCostsEnd>{self._format_decimal(asset.acquisition_cost)}</nsSAFT:AcquisitionAndProductionCostsEnd>
                <nsSAFT:InvestmentSupport>0.00</nsSAFT:InvestmentSupport>
                <nsSAFT:AssetLifeYear>{asset.useful_life_months / 12 if asset.useful_life_months else 5}</nsSAFT:AssetLifeYear>
                <nsSAFT:AssetAddition>0.00</nsSAFT:AssetAddition>
                <nsSAFT:Transfers>0.00</nsSAFT:Transfers>
                <nsSAFT:AssetDisposal>0.00</nsSAFT:AssetDisposal>
                <nsSAFT:BookValueBegin>{self._format_decimal(asset.book_value_begin_year or asset.acquisition_cost)}</nsSAFT:BookValueBegin>
                <nsSAFT:DepreciationMethod>{asset.depreciation_method or "Линеен"}</nsSAFT:DepreciationMethod>
                <nsSAFT:DepreciationPercentage>{depreciation_rate}</nsSAFT:DepreciationPercentage>
                <nsSAFT:DepreciationForPeriod>{self._format_decimal(asset.depreciation_for_period or Decimal(0))}</nsSAFT:DepreciationForPeriod>
                <nsSAFT:AppreciationForPeriod>0.00</nsSAFT:AppreciationForPeriod>
                <nsSAFT:AccumulatedDepreciation>{self._format_decimal(asset.accumulated_depreciation or Decimal(0))}</nsSAFT:AccumulatedDepreciation>
                <nsSAFT:BookValueEnd>{self._format_decimal(asset.book_value or asset.acquisition_cost)}</nsSAFT:BookValueEnd>
              </nsSAFT:ValuationSAP>
              <nsSAFT:ValuationDAP>
                <nsSAFT:ValuationClass>{asset.tax_category or "V"}</nsSAFT:ValuationClass>
                <nsSAFT:CategoryTaxDepreciable>ДМА</nsSAFT:CategoryTaxDepreciable>
                <nsSAFT:TaxDepreciableValue>{self._format_decimal(asset.acquisition_cost)}</nsSAFT:TaxDepreciableValue>
                <nsSAFT:AccruedTaxDepreciation>{self._format_decimal(asset.accumulated_depreciation or Decimal(0))}</nsSAFT:AccruedTaxDepreciation>
                <nsSAFT:TaxValueAsset>{self._format_decimal(asset.book_value or asset.acquisition_cost)}</nsSAFT:TaxValueAsset>
                <nsSAFT:AnnualTaxDepreciationRate>{tax_depreciation_rate}</nsSAFT:AnnualTaxDepreciationRate>
                <nsSAFT:MonthChangeAssetValue>{asset.month_value_change or 0}</nsSAFT:MonthChangeAssetValue>
                <nsSAFT:MonthSuspensionResumptionAccrual>{asset.month_suspension_resumption or 0}</nsSAFT:MonthSuspensionResumptionAccrual>
                <nsSAFT:MonthWriteOffAccounting>{asset.month_writeoff_accounting or 0}</nsSAFT:MonthWriteOffAccounting>
                <nsSAFT:MonthWriteOffTax>{asset.month_writeoff_tax or 0}</nsSAFT:MonthWriteOffTax>
                <nsSAFT:NumberMonthsDepreciationDuring>{asset.depreciation_months_current_year or 12}</nsSAFT:NumberMonthsDepreciationDuring>
                <nsSAFT:DepreciationForPeriod>{self._format_decimal(asset.depreciation_for_period or Decimal(0))}</nsSAFT:DepreciationForPeriod>
                <nsSAFT:AccumulatedDepreciation>{self._format_decimal(asset.accumulated_depreciation or Decimal(0))}</nsSAFT:AccumulatedDepreciation>
                <nsSAFT:TaxValueEndPeriod>{self._format_decimal(asset.book_value or asset.acquisition_cost)}</nsSAFT:TaxValueEndPeriod>
              </nsSAFT:ValuationDAP>
            </nsSAFT:Valuations>
        """

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

    def _format_eik(self, eik: Optional[str]) -> str:
        if not eik:
            return ""
        return eik.zfill(12)

    def _get_contraagents(self, is_customer: bool = False, is_supplier: bool = False) -> List[Contraagent]:
        """Retrieve contraagents filtered by customer/supplier status."""
        with Session(self.organization.engine) as session:
            statement = select(Contraagent).where(Contraagent.organization_id == self.organization.id)
            if is_customer:
                statement = statement.where(Contraagent.is_customer == True)
            if is_supplier:
                statement = statement.where(Contraagent.is_supplier == True)
            return session.exec(statement).all()

    def _get_products(self) -> List[Product]:
        """Retrieve products for the organization."""
        with Session(self.organization.engine) as session:
            return session.exec(select(Product).where(Product.organization_id == self.organization.id)).all()

    def _get_accounts_with_balances(self) -> List[Any]:
        """Retrieve accounts for the organization with calculated balances."""
        with Session(self.organization.engine) as session:
            accounts = session.exec(select(Account).where(Account.organization_id == self.organization.id)).all()

            start_date_period = date(self.year, self.month, 1)
            end_date_period = (start_date_period.replace(day=28) + timedelta(days=4))
            end_date_period -= timedelta(days=end_date_period.day)

            start_date_year = date(self.year, 1, 1)

            accounts_with_balances = []
            for account in accounts:
                # Calculate transactions before the period (for opening balance)
                stmt_before = (
                    select(func.sum(EntryLine.debit), func.sum(EntryLine.credit))
                    .join(JournalEntry)
                    .where(EntryLine.account_id == account.id)
                    .where(JournalEntry.entry_date >= start_date_year)
                    .where(JournalEntry.entry_date < start_date_period)
                )
                sum_debit_before, sum_credit_before = session.exec(stmt_before).first()
                sum_debit_before = Decimal(str(sum_debit_before or 0.0))
                sum_credit_before = Decimal(str(sum_credit_before or 0.0))

                opening_balance = Decimal(str(account.opening_balance)) + sum_debit_before - sum_credit_before

                # Calculate transactions within the period
                stmt_period = (
                    select(func.sum(EntryLine.debit), func.sum(EntryLine.credit))
                    .join(JournalEntry)
                    .where(EntryLine.account_id == account.id)
                    .where(JournalEntry.entry_date >= start_date_period)
                    .where(JournalEntry.entry_date <= end_date_period)
                )
                sum_debit_period, sum_credit_period = session.exec(stmt_period).first()
                sum_debit_period = Decimal(str(sum_debit_period or 0.0))
                sum_credit_period = Decimal(str(sum_credit_period or 0.0))

                closing_balance = opening_balance + sum_debit_period - sum_credit_period

                accounts_with_balances.append({
                    "account": account,
                    "opening_balance": opening_balance,
                    "closing_balance": closing_balance
                })

            return accounts_with_balances


    def _get_assets(self) -> List[Asset]:
        """Retrieve assets for the organization."""
        with Session(self.organization.engine) as session:
            return session.exec(select(Asset).where(Asset.organization_id == self.organization.id)).all()

    def _get_journal_entries(self) -> List[JournalEntry]:
        """Retrieve journal entries for the organization filtered by year/month."""
        with Session(self.organization.engine) as session:
            statement = select(JournalEntry).where(
                JournalEntry.organization_id == self.organization.id,
                func.extract("year", JournalEntry.date) == self.year
            )
            if self.month:
                statement = statement.where(func.extract("month", JournalEntry.date) == self.month)
            return session.exec(statement).all()

    def _get_entry_lines_for_journal_entry(self, journal_entry_id: UUID) -> List[EntryLine]:
        """Retrieve entry lines for a specific journal entry."""
        with Session(self.organization.engine) as session:
            return session.exec(
                select(EntryLine).where(EntryLine.journal_entry_id == journal_entry_id)
            ).all()
