import httpx
from app.core.config import settings

class PdfService:
    @staticmethod
    async def generate_invoice_pdf(invoice_data: dict) -> bytes:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{settings.ELIXIR_APP_URL}/api/invoices/generate_pdf",
                json={"invoice_data": invoice_data},
                timeout=30.0,
            )
            response.raise_for_status()
            return response.content
