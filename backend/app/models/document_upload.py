import uuid
import enum
from datetime import datetime
from typing import Optional, TYPE_CHECKING

from sqlmodel import Field, Relationship, JSON, Column

from app.models.base import BaseModel
from app.utils import utcnow

if TYPE_CHECKING:
    from app.models.organization import Organization
    from app.models.user import User
    from .extracted_invoice import ExtractedInvoice


class DocumentUploadStatus(str, enum.Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


class DocumentUploadBase(BaseModel):
    original_filename: str = Field(max_length=255)
    local_path: Optional[str] = Field(default=None, max_length=1024)
    file_size: Optional[int] = None
    file_type: Optional[str] = Field(default=None, max_length=255)
    status: DocumentUploadStatus = Field(default=DocumentUploadStatus.PENDING)
    document_type: Optional[str] = Field(default=None, max_length=50)
    processed_at: Optional[datetime] = None
    error_message: Optional[str] = None
    azure_document_id: Optional[str] = Field(default=None, max_length=255)
    azure_result: Optional[dict] = Field(default=None, sa_column=Column(JSON))


class DocumentUpload(DocumentUploadBase, table=True):
    __tablename__ = "document_uploads"
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    organization_id: uuid.UUID = Field(
        foreign_key="organization.id", nullable=False, index=True
    )
    created_by_id: uuid.UUID = Field(foreign_key="user.id", nullable=False)

    date_created: datetime = Field(default_factory=utcnow)
    date_updated: datetime = Field(default_factory=utcnow)

    organization: "Organization" = Relationship()
    created_by: "User" = Relationship()

    extracted_invoice: Optional["ExtractedInvoice"] = Relationship(back_populates="document_upload")


class DocumentUploadCreate(DocumentUploadBase):
    organization_id: uuid.UUID
    created_by_id: uuid.UUID


class DocumentUploadUpdate(BaseModel):
    status: Optional[DocumentUploadStatus] = None
    processed_at: Optional[datetime] = None
    error_message: Optional[str] = None
    azure_document_id: Optional[str] = None
    azure_result: Optional[dict] = None


class DocumentUploadPublic(DocumentUploadBase):
    id: uuid.UUID
    date_created: datetime
