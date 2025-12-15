"""CRUD operations for Organization Settings."""
import uuid
from datetime import datetime

from sqlmodel import Session, select

from app.models import (
    OrganizationSettings,
    OrganizationSettingsCreate,
    OrganizationSettingsUpdate,
    SmtpSettingsUpdate,
    AzureSettingsUpdate,
    DefaultAccountsUpdate,
)
from app.utils import utcnow


def get_by_organization(
    *, session: Session, organization_id: uuid.UUID
) -> OrganizationSettings | None:
    """Get settings for an organization."""
    statement = select(OrganizationSettings).where(
        OrganizationSettings.organization_id == organization_id
    )
    return session.exec(statement).first()


def create_settings(
    *, session: Session, settings_in: OrganizationSettingsCreate, organization_id: uuid.UUID
) -> OrganizationSettings:
    """Create new organization settings."""
    db_settings = OrganizationSettings.model_validate(
        settings_in,
        update={"organization_id": organization_id}
    )
    session.add(db_settings)
    session.commit()
    session.refresh(db_settings)
    return db_settings


def update_settings(
    *, session: Session, db_settings: OrganizationSettings, settings_in: OrganizationSettingsUpdate
) -> OrganizationSettings:
    """Update organization settings."""
    update_data = settings_in.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_settings, field, value)
    db_settings.date_updated = utcnow()
    session.add(db_settings)
    session.commit()
    session.refresh(db_settings)
    return db_settings


def get_or_create(
    *, session: Session, organization_id: uuid.UUID
) -> OrganizationSettings:
    """Get existing settings or create default ones."""
    settings = get_by_organization(session=session, organization_id=organization_id)
    if not settings:
        settings = OrganizationSettings(organization_id=organization_id)
        session.add(settings)
        session.commit()
        session.refresh(settings)
    return settings


def update_smtp_settings(
    *, session: Session, organization_id: uuid.UUID, smtp_in: SmtpSettingsUpdate
) -> OrganizationSettings:
    """Update only SMTP settings."""
    settings = get_or_create(session=session, organization_id=organization_id)
    update_data = smtp_in.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(settings, field, value)
    settings.date_updated = utcnow()
    session.add(settings)
    session.commit()
    session.refresh(settings)
    return settings


def update_azure_settings(
    *, session: Session, organization_id: uuid.UUID, azure_in: AzureSettingsUpdate
) -> OrganizationSettings:
    """Update only Azure Document Intelligence settings."""
    settings = get_or_create(session=session, organization_id=organization_id)
    update_data = azure_in.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(settings, field, value)
    settings.date_updated = utcnow()
    session.add(settings)
    session.commit()
    session.refresh(settings)
    return settings


def update_default_accounts(
    *, session: Session, organization_id: uuid.UUID, accounts_in: DefaultAccountsUpdate
) -> OrganizationSettings:
    """Update only default accounts."""
    settings = get_or_create(session=session, organization_id=organization_id)
    update_data = accounts_in.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(settings, field, value)
    settings.date_updated = utcnow()
    session.add(settings)
    session.commit()
    session.refresh(settings)
    return settings
