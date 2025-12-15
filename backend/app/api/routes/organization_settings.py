"""API routes for Organization Settings."""
import smtplib
from email.mime.text import MIMEText
from typing import Any

from fastapi import APIRouter, HTTPException

from app.api.deps import (
    CurrentUser,
    CurrentOrganization,
    RequireAdmin,
    SessionDep,
)
from app.crud import organization_settings as settings_crud
from app.models import (
    OrganizationSettingsPublic,
    OrganizationSettingsUpdate,
    SmtpSettingsUpdate,
    AzureSettingsUpdate,
    DefaultAccountsUpdate,
    SmtpTestResult,
)

router = APIRouter(prefix="/organization-settings", tags=["organization-settings"])


@router.get("", response_model=OrganizationSettingsPublic)
def get_settings(
    db: SessionDep,
    current_user: CurrentUser,
    current_org: CurrentOrganization,
) -> Any:
    """
    Get organization settings.
    Creates default settings if they don't exist.
    """
    settings = settings_crud.get_or_create(
        session=db, organization_id=current_org.id
    )
    return settings


@router.put("", response_model=OrganizationSettingsPublic)
def update_settings(
    db: SessionDep,
    current_user: CurrentUser,
    current_org: CurrentOrganization,
    _: RequireAdmin,  # Only admins can update settings
    settings_in: OrganizationSettingsUpdate,
) -> Any:
    """
    Update organization settings.
    Requires admin role.
    """
    settings = settings_crud.get_or_create(
        session=db, organization_id=current_org.id
    )
    updated = settings_crud.update_settings(
        session=db, db_settings=settings, settings_in=settings_in
    )
    return updated


@router.put("/smtp", response_model=OrganizationSettingsPublic)
def update_smtp_settings(
    db: SessionDep,
    current_user: CurrentUser,
    current_org: CurrentOrganization,
    _: RequireAdmin,
    smtp_in: SmtpSettingsUpdate,
) -> Any:
    """
    Update SMTP settings only.
    Requires admin role.
    """
    settings = settings_crud.update_smtp_settings(
        session=db, organization_id=current_org.id, smtp_in=smtp_in
    )
    return settings


@router.put("/azure", response_model=OrganizationSettingsPublic)
def update_azure_settings(
    db: SessionDep,
    current_user: CurrentUser,
    current_org: CurrentOrganization,
    _: RequireAdmin,
    azure_in: AzureSettingsUpdate,
) -> Any:
    """
    Update Azure Document Intelligence settings only.
    Requires admin role.
    """
    settings = settings_crud.update_azure_settings(
        session=db, organization_id=current_org.id, azure_in=azure_in
    )
    return settings


@router.put("/accounts", response_model=OrganizationSettingsPublic)
def update_default_accounts(
    db: SessionDep,
    current_user: CurrentUser,
    current_org: CurrentOrganization,
    _: RequireAdmin,
    accounts_in: DefaultAccountsUpdate,
) -> Any:
    """
    Update default accounting accounts only.
    Requires admin role.
    """
    settings = settings_crud.update_default_accounts(
        session=db, organization_id=current_org.id, accounts_in=accounts_in
    )
    return settings


@router.post("/smtp/test", response_model=SmtpTestResult)
def test_smtp_connection(
    db: SessionDep,
    current_user: CurrentUser,
    current_org: CurrentOrganization,
    _: RequireAdmin,
) -> Any:
    """
    Test SMTP connection with current settings.
    Requires admin role.
    """
    settings = settings_crud.get_by_organization(
        session=db, organization_id=current_org.id
    )

    if not settings:
        return SmtpTestResult(
            success=False,
            message="Няма конфигурирани SMTP настройки / No SMTP settings configured"
        )

    if not settings.smtp_host:
        return SmtpTestResult(
            success=False,
            message="SMTP хост не е зададен / SMTP host is not set"
        )

    try:
        # Try to connect to the SMTP server
        if settings.smtp_use_tls:
            server = smtplib.SMTP(settings.smtp_host, settings.smtp_port or 587)
            server.starttls()
        else:
            server = smtplib.SMTP(settings.smtp_host, settings.smtp_port or 25)

        # Try to login if credentials are provided
        if settings.smtp_username and settings.smtp_password:
            server.login(settings.smtp_username, settings.smtp_password)

        server.quit()

        return SmtpTestResult(
            success=True,
            message="Успешна връзка с SMTP сървъра / SMTP connection successful"
        )

    except smtplib.SMTPAuthenticationError:
        return SmtpTestResult(
            success=False,
            message="Грешка при удостоверяване - проверете потребител и парола / Authentication error - check username and password"
        )
    except smtplib.SMTPConnectError:
        return SmtpTestResult(
            success=False,
            message="Неуспешна връзка със сървъра - проверете хост и порт / Connection failed - check host and port"
        )
    except Exception as e:
        return SmtpTestResult(
            success=False,
            message=f"Грешка / Error: {str(e)}"
        )
