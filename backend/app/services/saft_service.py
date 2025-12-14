from datetime import date
from typing import IO, Any, Dict, Optional

from app.core.config import settings
from app.models.organization import Organization
from app.services.saft.header import SAFTHeader
from app.services.saft.master_files import SAFTMasterFiles
from app.services.saft.general_ledger_entries import SAFTGeneralLedgerEntries
from app.services.saft.source_documents import SAFTSourceDocuments
from app.services.saft import constants


class SAFT:
    """
    Main class for generating SAF-T files.
    """

    def __init__(self, organization: Organization, year: int, month: Optional[int] = None):
        self.organization = organization
        self.year = year
        self.month = month
        self.settings = settings

    def generate(self, report_type: str, output: IO[Any], **kwargs):
        """
        Generate a SAF-T file of the specified type.
        """
        if report_type not in ["annual", "monthly", "on_demand"]:
            raise ValueError("Invalid report type")

        output.write(f'<nsSAFT:AuditFile xmlns:doc="urn:schemas-OECD:schema-extensions:documentation xml:lang=en" xmlns:nsSAFT="{constants.NAMESPACE}" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">')

        header_generator = SAFTHeader(self.organization, self.year, self.month)
        header_generator.generate(output, report_type=report_type, **kwargs)

        master_files_generator = SAFTMasterFiles(self.organization, self.year, self.month)
        master_files_generator.generate(output, report_type=report_type, **kwargs)

        if report_type == "monthly":
            gl_entries_generator = SAFTGeneralLedgerEntries(self.organization, self.year, self.month)
            gl_entries_generator.generate(output, **kwargs)

        source_documents_generator = SAFTSourceDocuments(self.organization, self.year, self.month)
        source_documents_generator.generate(output, report_type=report_type, **kwargs)

        output.write('</nsSAFT:AuditFile>')

