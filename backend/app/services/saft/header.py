
import html
from datetime import date
from typing import IO, Any, Optional, Tuple

from app.models.organization import Organization
from app.services.saft import constants


class SAFTHeader:
    def __init__(self, organization: Organization, year: int, month: Optional[int] = None):
        self.organization = organization
        self.year = year
        self.month = month

    def generate(self, output: IO[Any], report_type: str, **kwargs: Any):
        if report_type == "monthly":
            header_comment = "M"
            selection_criteria = self._build_monthly_selection_criteria()
        elif report_type == "annual":
            header_comment = "A"
            selection_criteria = self._build_annual_selection_criteria()
        elif report_type == "on_demand":
            header_comment = "D"
            selection_criteria = self._build_on_demand_selection_criteria(**kwargs)
        else:
            raise ValueError("Invalid report type")

        header = self._build_header(selection_criteria, header_comment)
        output.write(header)

    def _build_monthly_selection_criteria(self) -> str:
        return f"""
        <nsSAFT:SelectionCriteria>
          <nsSAFT:TaxReportingJurisdiction>NRA</nsSAFT:TaxReportingJurisdiction>
          <nsSAFT:CompanyEntity/>
          <nsSAFT:PeriodStart>{self.month}</nsSAFT:PeriodStart>
          <nsSAFT:PeriodStartYear>{self.year}</nsSAFT:PeriodStartYear>
          <nsSAFT:PeriodEnd>{self.month}</nsSAFT:PeriodEnd>
          <nsSAFT:PeriodEndYear>{self.year}</nsSAFT:PeriodEndYear>
          <nsSAFT:DocumentType/>
          <nsSAFT:OtherCriteria/>
        </nsSAFT:SelectionCriteria>
        """

    def _build_annual_selection_criteria(self) -> str:
        return f"""
        <nsSAFT:SelectionCriteria>
          <nsSAFT:TaxReportingJurisdiction>NRA</nsSAFT:TaxReportingJurisdiction>
          <nsSAFT:CompanyEntity/>
          <nsSAFT:SelectionStartDate>{self.year}-01-01</nsSAFT:SelectionStartDate>
          <nsSAFT:SelectionEndDate>{self.year}-12-31</nsSAFT:SelectionEndDate>
          <nsSAFT:DocumentType/>
          <nsSAFT:OtherCriteria/>
        </nsSAFT:SelectionCriteria>
        """

    def _build_on_demand_selection_criteria(self, start_date: date, end_date: date) -> str:
        return f"""
        <nsSAFT:SelectionCriteria>
          <nsSAFT:TaxReportingJurisdiction>NRA</nsSAFT:TaxReportingJurisdiction>
          <nsSAFT:CompanyEntity/>
          <nsSAFT:SelectionStartDate>{start_date.isoformat()}</nsSAFT:SelectionStartDate>
          <nsSAFT:SelectionEndDate>{end_date.isoformat()}</nsSAFT:SelectionEndDate>
          <nsSAFT:DocumentType/>
          <nsSAFT:OtherCriteria/>
        </nsSAFT:SelectionCriteria>
        """

    def _build_header(self, selection_criteria: str, header_comment: str) -> str:
        today = date.today().isoformat()
        region = self._get_region()
        return f"""
      <nsSAFT:Header>
        <nsSAFT:AuditFileVersion>{constants.SCHEMA_VERSION}</nsSAFT:AuditFileVersion>
        <nsSAFT:AuditFileCountry>{constants.COUNTRY}</nsSAFT:AuditFileCountry>
        <nsSAFT:AuditFileRegion>{region}</nsSAFT:AuditFileRegion>
        <nsSAFT:AuditFileDateCreated>{today}</nsSAFT:AuditFileDateCreated>
        <nsSAFT:SoftwareCompanyName>Barasurya</nsSAFT:SoftwareCompanyName>
        <nsSAFT:SoftwareID>Barasurya</nsSAFT:SoftwareID>
        <nsSAFT:SoftwareVersion>1.0</nsSAFT:SoftwareVersion>
    {self._build_company()}
    {self._build_ownership()}
        <nsSAFT:DefaultCurrencyCode>{self._get_currency()}</nsSAFT:DefaultCurrencyCode>
    {selection_criteria}
        <nsSAFT:HeaderComment>{header_comment}</nsSAFT:HeaderComment>
        <nsSAFT:TaxAccountingBasis>{self._get_tax_basis()}</nsSAFT:TaxAccountingBasis>
        <nsSAFT:TaxEntity>{self.organization.name or "Company"}</nsSAFT:TaxEntity>
      </nsSAFT:Header>
        """

    def _build_company(self) -> str:
        return f"""
        <nsSAFT:Company>
          <nsSAFT:RegistrationNumber>{self._format_eik()}</nsSAFT:RegistrationNumber>
          <nsSAFT:Name>{self._escape_xml(self.organization.name)}</nsSAFT:Name>
    {self._build_address()}
    {self._build_contact()}
    {self._build_tax_registration()}
    {self._build_bank_account()}
        </nsSAFT:Company>
        """

    def _build_address(self) -> str:
        street = self.organization.street_name or ""
        number = self.organization.building_number or ""
        city = self.organization.city or ""
        postal_code = self.organization.postal_code or ""
        country = self.organization.country or "BG"
        region = self.organization.region or ""
        return f"""
          <nsSAFT:Address>
            <nsSAFT:StreetName>{self._escape_xml(street)}</nsSAFT:StreetName>
            <nsSAFT:Number>{self._escape_xml(number)}</nsSAFT:Number>
            <nsSAFT:AdditionalAddressDetail/>
            <nsSAFT:Building>{self._escape_xml(self.organization.building or "")}</nsSAFT:Building>
            <nsSAFT:City>{self._escape_xml(city)}</nsSAFT:City>
            <nsSAFT:PostalCode>{postal_code}</nsSAFT:PostalCode>
            <nsSAFT:Region>{self._escape_xml(region)}</nsSAFT:Region>
            <nsSAFT:Country>{country}</nsSAFT:Country>
            <nsSAFT:AddressType>StreetAddress</nsSAFT:AddressType>
          </nsSAFT:Address>
        """

    def _build_contact(self) -> str:
        contact_name = self.organization.legal_representative_name or ""
        contact_phone = self.organization.phone or ""
        contact_email = self.organization.email or ""
        website = self.organization.website or ""
        first_name, last_name = self._split_name(contact_name)
        return f"""
          <nsSAFT:Contact>
            <nsSAFT:ContactPerson>
              <nsSAFT:Title/>
              <nsSAFT:FirstName>{self._escape_xml(first_name)}</nsSAFT:FirstName>
              <nsSAFT:Initials/>
              <nsSAFT:LastNamePrefix/>
              <nsSAFT:LastName>{self._escape_xml(last_name)}</nsSAFT:LastName>
              <nsSAFT:BirthName/>
              <nsSAFT:Salutation/>
              <nsSAFT:OtherTitles>{self._escape_xml(contact_name)}</nsSAFT:OtherTitles>
            </nsSAFT:ContactPerson>
            <nsSAFT:Telephone>{contact_phone}</nsSAFT:Telephone>
            <nsSAFT:Fax/>
            <nsSAFT:Email>{contact_email}</nsSAFT:Email>
            <nsSAFT:Website>{website}</nsSAFT:Website>
          </nsSAFT:Contact>
        """

    def _build_tax_registration(self) -> str:
        eik = self.organization.registration_number or ""
        vat_number = self.organization.vat_number or ""
        tax_type = "100020"
        tax_authority = self.organization.tax_authority or "NRA"
        return f"""
          <nsSAFT:TaxRegistration>
            <nsSAFT:TaxRegistrationNumber>{eik}</nsSAFT:TaxRegistrationNumber>
            <nsSAFT:TaxType>{tax_type}</nsSAFT:TaxType>
            <nsSAFT:TaxNumber>{vat_number}</nsSAFT:TaxNumber>
            <nsSAFT:TaxAuthority>{tax_authority}</nsSAFT:TaxAuthority>
            <nsSAFT:TaxVerificationDate>{date.today().isoformat()}</nsSAFT:TaxVerificationDate>
          </nsSAFT:TaxRegistration>
        """

    def _build_bank_account(self) -> str:
        iban = self.organization.bank_iban or ""
        return f"""
        <nsSAFT:BankAccount>
          <nsSAFT:IBANNumber>{iban}</nsSAFT:IBANNumber>
        </nsSAFT:BankAccount>
        """

    def _build_ownership(self) -> str:
        owner_name = self.organization.legal_representative_name or ""
        owner_egn = self.organization.legal_representative_id or ""
        return f"""
        <nsSAFT:Ownership>
          <nsSAFT:IsPartOfGroup>1</nsSAFT:IsPartOfGroup>
          <nsSAFT:BeneficialOwnerNameCyrillicBG>{self._escape_xml(owner_name)}</nsSAFT:BeneficialOwnerNameCyrillicBG>
          <nsSAFT:BeneficialOwnerEGN>{owner_egn}</nsSAFT:BeneficialOwnerEGN>
          <nsSAFT:UltimateOwnerNameCyrillicBG></nsSAFT:UltimateOwnerNameCyrillicBG>
          <nsSAFT:UltimateOwnerUICBG></nsSAFT:UltimateOwnerUICBG>
          <nsSAFT:UltimateOwnerNameCyrillicForeign></nsSAFT:UltimateOwnerNameCyrillicForeign>
          <nsSAFT:UltimateOwnerNameLatinForeign></nsSAFT:UltimateOwnerNameLatinForeign>
          <nsSAFT:CountryForeign>BG</nsSAFT:CountryForeign>
        </nsSAFT:Ownership>
        """

    def _format_eik(self) -> str:
        eik = self.organization.registration_number or ""
        return eik.zfill(12)

    def _get_region(self) -> str:
        # The SAF-T region is expected to be a 2-digit code.
        # The Organization.region field should store this code.
        region_code = self.organization.region or "22"
        return f"BG-{region_code}"

    def _get_currency(self) -> str:
        return self.organization.currency_code or "BGN"

    def _get_tax_basis(self) -> str:
        return self.organization.tax_accounting_basis or "A"

    def _split_name(self, full_name: str) -> Tuple[str, str]:
        if not full_name:
            return "", ""
        parts = full_name.split(" ", 1)
        if len(parts) == 1:
            return parts[0], ""
        return parts[0], parts[1]

    def _escape_xml(self, text: Optional[str]) -> str:
        if not text:
            return ""
        return html.escape(text)

