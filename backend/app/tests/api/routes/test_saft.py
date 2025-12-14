
from fastapi.testclient import TestClient
from sqlmodel import Session

from app.core.config import settings
from app.tests.conftest import authentication_token_from_email
from app.tests.utils.user import create_random_user


def test_generate_saft_monthly(client: TestClient, db: Session) -> None:
    user = create_random_user(db=db)
    user_token_headers = authentication_token_from_email(
        client=client, email=user.email, db=db
    )
    response = client.get(
        f"{settings.API_V1_STR}/saft/?report_type=monthly&year=2025&month=1",
        headers=user_token_headers,
    )
    assert response.status_code == 200
    assert response.headers["content-type"] == "application/xml"
    assert "attachment; filename=saft_monthly.xml" in response.headers["content-disposition"]
    assert response.text.startswith("<nsSAFT:AuditFile")
