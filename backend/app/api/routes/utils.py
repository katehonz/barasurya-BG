from fastapi import APIRouter, Depends
from pydantic.networks import EmailStr
from typing import List

from app.api.deps import get_current_active_superuser
from app.models import Message
from app.schemas.utils import InvoiceType
from app.utils import generate_test_email, send_email

router = APIRouter(prefix="/utils", tags=["utils"])


@router.post(
    "/test-email/",
    dependencies=[Depends(get_current_active_superuser)],
    status_code=201,
)
def test_email(email_to: EmailStr) -> Message:
    """
    Test emails.
    """
    email_data = generate_test_email(email_to=email_to)
    send_email(
        email_to=email_to,
        subject=email_data.subject,
        html_content=email_data.html_content,
    )
    return Message(message="Test email sent")


@router.get("/health-check/")
async def health_check() -> bool:
    return True

@router.get("/invoice-types/", response_model=List[InvoiceType])
def read_invoice_types() -> List[InvoiceType]:
    """
    Retrieve invoice types.
    """
    invoice_types = [
        {"code": "01", "name": "Фактура"},
        {"code": "02", "name": "Дебитно известие"},
        {"code": "03", "name": "Кредитно известие"},
        {"code": "04", "name": "Регистър на стоки под режим складиране на стоки до поискване, изпратени или транспортирани от територията на страната до територията на друга държава членка"},
        {"code": "05", "name": "Регистър на стоки под режим складиране на стоки до поискване, получени на територията на страната"},
        {"code": "07", "name": "Митническа декларация"},
        {"code": "09", "name": "Протокол или друг документ"},
        {"code": "11", "name": "Фактура - касова отчетност"},
        {"code": "12", "name": "Дебитно известие – касова отчетност"},
        {"code": "13", "name": "Кредитно известие – касова отчетност"},
        {"code": "23", "name": "Кредитно известие по чл. 126б, ал. 1 от ЗДДС"},
        {"code": "29", "name": "Протокол по чл. 126б, ал. 2 и 7 от ЗДДС"},
        {"code": "81", "name": "Отчет за извършените продажби"},
        {"code": "82", "name": "Отчет за извършените продажби при специален ред на облагане"},
        {"code": "91", "name": "Протокол за изискуемия данък по чл. 151в, ал. 3 от закона"},
        {"code": "92", "name": "Протокол за данъчния кредит по чл. 151г, ал. 8 от закона или отчет по чл. 104ж, ал. 14"},
        {"code": "93", "name": "Протокол за изискуемия данък по чл. 151в, ал. 7 от закона с получател по доставката лице, което не прилага специалния режим"},
        {"code": "94", "name": "Протокол за изискуемия данък по чл. 151в, ал. 7 от закона с получател по доставката лице, което прилага специалния режим"},
        {"code": "95", "name": "Протокол за безвъзмездно предоставяне на хранителни стоки, за което е приложим чл. 6, ал. 4, т. 4 ЗДДС"},
    ]
    return invoice_types
