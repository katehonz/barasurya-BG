import html
from datetime import date, timedelta
from decimal import Decimal
from typing import IO, Any, List, Optional, Tuple
from uuid import UUID

from sqlalchemy.orm import selectinload
from sqlmodel import Session, func, select

from app.models.account import Account
from app.models.asset import Asset
from app.models.customer import Customer
from app.models.entry_line import EntryLine
from app.models.journal_entry import JournalEntry
from app.models.organization import Organization
from app.models.item import Item
from app.models.supplier import Supplier


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

    def _build_account(self, account: Any) -> str:
        # TODO: Get account type and balance
        account_type = "Bifunctional"
        opening_balance = "0.00"
        closing_balance = "0.00"
        return f"""
          <nsSAFT:Account>
            <nsSAFT:AccountID>{account.code}</nsSAFT:AccountID>
            <nsSAFT:AccountDescription>{self._escape_xml(account.name)}</nsSAFT:AccountDescription>
            <nsSAFT:TaxpayerAccountID>{account.standard_code or account.code}</nsSAFT:TaxpayerAccountID>
            <nsSAFT:AccountType>{account_type}</nsSAFT:AccountType>
            <nsSAFT:AccountCreationDate>{self._format_date(account.inserted_at)}</nsSAFT:AccountCreationDate>
            <nsSAFT:OpeningDebitBalance>{opening_balance}</nsSAFT:OpeningDebitBalance>
            <nsSAFT:ClosingDebitBalance>{closing_balance}</nsSAFT:ClosingDebitBalance>
          </nsSAFT:Account>
        """

    def _build_customers(self) -> str:
        customers = self._get_customers()
        customers_xml = "\n".join([self._build_customer(customer) for customer in customers])
        return f"""
      <nsSAFT:Customers>
  {customers_xml}
      </nsSAFT:Customers>
        """
    def _build_customer(self, customer: Any) -> str:
        opening_balance = customer.opening_debit_balance or Decimal(0)
        closing_balance = customer.closing_debit_balance or Decimal(0)
        return f"""
          <nsSAFT:Customer>
    {self._build_company_structure(customer)}
            <nsSAFT:CustomerID>{customer.registration_number or customer.id}</nsSAFT:CustomerID>
            <nsSAFT:SelfBillingIndicator>{"Y" if customer.self_billing_indicator else "N"}</nsSAFT:SelfBillingIndicator>
            <nsSAFT:AccountID>411</nsSAFT:AccountID>
            <nsSAFT:OpeningDebitBalance>{self._format_decimal(opening_balance)}</nsSAFT:OpeningDebitBalance>
            <nsSAFT:ClosingDebitBalance>{self._format_decimal(closing_balance)}</nsSAFT:ClosingDebitBalance>
          </nsSAFT:Customer>
        """

    def _build_suppliers(self) -> str:
        suppliers = self._get_suppliers()
        suppliers_xml = "\n".join([self._build_supplier(supplier) for supplier in suppliers])
        return f"""
      <nsSAFT:Suppliers>
  {suppliers_xml}
      </nsSAFT:Suppliers>
        """

    def _build_supplier(self, supplier: Any) -> str:
        opening_balance = supplier.opening_credit_balance or Decimal(0)
        closing_balance = supplier.closing_credit_balance or Decimal(0)
        return f"""
          <nsSAFT:Supplier>
    {self._build_company_structure(supplier)}
            <nsSAFT:SupplierID>{supplier.registration_number or supplier.id}</nsSAFT:SupplierID>
            <nsSAFT:SelfBillingIndicator>{"Y" if supplier.self_billing_indicator else "N"}</nsSAFT:SelfBillingIndicator>
            <nsSAFT:AccountID>401</nsSAFT:AccountID>
            <nsSAFT:OpeningCreditBalance>{self._format_decimal(opening_balance)}</nsSAFT:OpeningCreditBalance>
            <nsSAFT:ClosingCreditBalance>{self._format_decimal(closing_balance)}</nsSAFT:ClosingCreditBalance>
          </nsSAFT:Supplier>
        """

    def _build_company_structure(self, contact: Any) -> str:
        city = contact.city or "София"
        country = contact.country or "BG"
        street = contact.street_name or contact.address or ""
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

    def _build_product(self, product: Any) -> str:
        # TODO: Get cn_code and goods_services_id
        cn_code = ""
        goods_services_id = "G"
        return f"""
          <nsSAFT:Product>
            <nsSAFT:ProductCode>{product.sku or product.id}</nsSAFT:ProductCode>
            <nsSAFT:GoodsServicesID>{goods_services_id}</nsSAFT:GoodsServicesID>
            <nsSAFT:ProductGroup>{self._escape_xml(product.category or "")}</nsSAFT:ProductGroup>
            <nsSAFT:Description>{self._escape_xml(product.name)}</nsSAFT:Description>
            <nsSAFT:ProductCommodityCode>{cn_code}</nsSAFT:ProductCommodityCode>
            <nsSAFT:UOMBase>{product.unit or "PCE"}</nsSAFT:UOMBase>
            <nsSAFT:UOMStandard>{product.unit or "PCE"}</nsSAFT:UOMStandard>
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
    {self._build_asset_supplier(asset)}
            <nsSAFT:PurchaseOrderDate>{self._format_date(asset.purchase_order_date or asset.acquisition_date)}</nsSAFT:PurchaseOrderDate>
            <nsSAFT:DateOfAcquisition>{self._format_date(asset.acquisition_date)}</nsSAFT:DateOfAcquisition>
            <nsSAFT:StartUpDate>{self._format_date(asset.startup_date or asset.acquisition_date)}</nsSAFT:StartUpDate>
    {self._build_asset_valuations(asset)}
          </nsSAFT:Asset>
        """

    def _build_asset_supplier(self, asset: Any) -> str:
        if not asset.supplier:
            return ""
        return f"""
            <nsSAFT:AssetSupplier>
              <nsSAFT:SupplierName>{self._escape_xml(asset.supplier.name)}</nsSAFT:SupplierName>
              <nsSAFT:SupplierID>{asset.supplier.vat_number or asset.supplier.eik or ""}</nsSAFT:SupplierID>
              <nsSAFT:PostalAddress>
                <nsSAFT:City>{self._escape_xml(asset.supplier.city or "")}</nsSAFT:City>
                <nsSAFT:Country>{asset.supplier.country or "BG"}</nsSAFT:Country>
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