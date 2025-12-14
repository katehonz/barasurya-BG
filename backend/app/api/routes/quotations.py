"""
Quotation API endpoints - управление на оферти за продажба.
"""

import uuid
from typing import Any, List
from datetime import date

from fastapi import APIRouter, HTTPException, Query
from sqlmodel import func, select

from app.api.deps import (
    CurrentMembership,
    CurrentOrganization,
    CurrentUser,
    SessionDep,
)
from app.models import (
    BaseModelUpdate,
    Message,
    OrganizationRole,
    has_role_or_higher,
)
from app.models.quotation import (
    Quotation,
    QuotationCreate,
    QuotationPublic,
    QuotationUpdate,
    QuotationsPublic,
    QuotationStatus,
    QuotationPriority,
)
from app.models.quotation_line import (
    QuotationLine,
    QuotationLineCreate,
    QuotationLinePublic,
)
from app.models.contraagent import Contraagent
from app.models.product import Product
from app.services.document_numbering_service import (
    DocumentNumberingService,
    DocumentUIDService,
)
from app.utils import utcnow

router = APIRouter(prefix="/quotations", tags=["quotations"])


@router.get("/", response_model=QuotationsPublic)
def read_quotations(
    session: SessionDep,
    current_org: CurrentOrganization,
    membership: CurrentMembership,
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=100, ge=0, le=100),
    status: QuotationStatus | None = Query(default=None),
    contraagent_id: uuid.UUID | None = Query(default=None),
) -> Any:
    """
    Retrieve quotations for the current organization.
    """
    count_statement = (
        select(func.count())
        .select_from(Quotation)
        .where(Quotation.organization_id == current_org.id)
    )
    if status:
        count_statement = count_statement.where(Quotation.status == status)
    if contraagent_id:
        count_statement = count_statement.where(Quotation.contraagent_id == contraagent_id)
    count = session.exec(count_statement).one()

    statement = (
        select(Quotation)
        .where(Quotation.organization_id == current_org.id)
    )
    if status:
        statement = statement.where(Quotation.status == status)
    if contraagent_id:
        statement = statement.where(Quotation.contraagent_id == contraagent_id)
    statement = statement.offset(skip).limit(limit).order_by(Quotation.date_created.desc())
    quotations = session.exec(statement).all()

    # Convert to public schemas with related data
    quotations_public = []
    for q in quotations:
        # Load related lines
        lines_statement = select(QuotationLine).where(
            QuotationLine.quotation_id == q.id
        )
        lines = session.exec(lines_statement).all()

        q_dict = q.model_dump()
        q_dict["contraagent_name"] = q.contraagent.name if q.contraagent else None
        q_dict["quotation_lines"] = [
            QuotationLinePublic.model_validate(line) for line in lines
        ]
        quotations_public.append(QuotationPublic.model_validate(q_dict))

    return QuotationsPublic(data=quotations_public, count=count)


@router.get("/{id}", response_model=QuotationPublic)
def read_quotation(
    session: SessionDep,
    current_org: CurrentOrganization,
    membership: CurrentMembership,
    id: uuid.UUID,
) -> Any:
    """
    Get quotation by ID.
    """
    quotation = session.get(Quotation, id)
    if not quotation:
        raise HTTPException(status_code=404, detail="Quotation not found")
    if quotation.organization_id != current_org.id:
        raise HTTPException(status_code=403, detail="Not enough permissions")

    # Load related lines
    lines_statement = select(QuotationLine).where(
        QuotationLine.quotation_id == quotation.id
    )
    lines = session.exec(lines_statement).all()

    q_dict = quotation.model_dump()
    q_dict["contraagent_name"] = quotation.contraagent.name if quotation.contraagent else None
    q_dict["quotation_lines"] = [
        QuotationLinePublic.model_validate(line) for line in lines
    ]

    return QuotationPublic.model_validate(q_dict)


@router.post("/", response_model=QuotationPublic)
def create_quotation(
    *,
    session: SessionDep,
    current_user: CurrentUser,
    current_org: CurrentOrganization,
    membership: CurrentMembership,
    quotation_in: QuotationCreate,
) -> Any:
    """
    Create new quotation. Requires at least member role.
    """
    # Validate contraagent exists and belongs to organization
    contraagent = session.get(Contraagent, quotation_in.contraagent_id)
    if not contraagent or contraagent.organization_id != current_org.id:
        raise HTTPException(status_code=404, detail="Contraagent not found")
    if not contraagent.is_customer: # Check if contraagent is a customer
        raise HTTPException(status_code=403, detail="Contraagent is not a customer")

    # Validate products
    for line in quotation_in.quotation_lines:
        product = session.get(Product, line.product_id)
        if not product or product.organization_id != current_org.id:
            raise HTTPException(
                status_code=404, detail=f"Product {line.product_id} not found"
            )

    # Generate quotation number
    quotation_no = f"QT{current_org.quotation_next_number:010d}"
    document_uid = DocumentUIDService.generate_document_uid(
        "quotation", current_org.id, quotation_no
    )

    # Update next number
    current_org.quotation_next_number += 1
    session.add(current_org)

    # Create quotation
    q_data = quotation_in.model_dump(exclude={"quotation_lines"})
    quotation = Quotation(
        **q_data,
        quotation_no=quotation_no,
        document_uid=document_uid,
        organization_id=current_org.id,
        created_by_id=current_user.id,
    )
    session.add(quotation)
    session.flush()  # Get the ID

    # Create lines
    lines = []
    for line_data in quotation_in.quotation_lines:
        line = QuotationLine(
            **line_data.model_dump(),
            quotation_id=quotation.id,
        )
        session.add(line)
        lines.append(line)

    session.commit()
    session.refresh(quotation)

    q_dict = quotation.model_dump()
    q_dict["contraagent_name"] = contraagent.name
    q_dict["quotation_lines"] = [
        QuotationLinePublic.model_validate(line) for line in lines
    ]

    return QuotationPublic.model_validate(q_dict)


@router.put("/{id}", response_model=QuotationPublic)
def update_quotation(
    *,
    session: SessionDep,
    current_org: CurrentOrganization,
    membership: CurrentMembership,
    id: uuid.UUID,
    quotation_in: QuotationUpdate,
) -> Any:
    """
    Update a quotation. Requires at least manager role.
    """
    if not has_role_or_higher(membership.role, OrganizationRole.MANAGER):
        raise HTTPException(status_code=403, detail="Requires manager role")

    quotation = session.get(Quotation, id)
    if not quotation:
        raise HTTPException(status_code=404, detail="Quotation not found")
    if quotation.organization_id != current_org.id:
        raise HTTPException(status_code=403, detail="Not enough permissions")

    # Check if quotation can be updated
    if quotation.status in [
        QuotationStatus.ACCEPTED,
        QuotationStatus.REJECTED,
        QuotationStatus.EXPIRED,
        QuotationStatus.CONVERTED_TO_INVOICE,
    ]:
        raise HTTPException(
            status_code=400, detail="Cannot update quotation in current status"
        )

    if quotation_in.contraagent_id is not None: # Changed from customer_id
        contraagent = session.get(Contraagent, quotation_in.contraagent_id) # Changed from customer
        if not contraagent or contraagent.organization_id != current_org.id:
            raise HTTPException(status_code=404, detail="Contraagent not found")
        if not contraagent.is_customer: # Check if contraagent is a customer
            raise HTTPException(status_code=403, detail="Contraagent is not a customer")

    # Update main object
    update_dict = quotation_in.model_dump(exclude_unset=True, exclude={"quotation_lines"})
    update_dict.update(BaseModelUpdate().model_dump())
    quotation.sqlmodel_update(update_dict)
    session.add(quotation)

    # Update lines if provided
    if quotation_in.quotation_lines is not None:
        # Delete existing lines
        existing_lines = session.exec(
            select(QuotationLine).where(
                QuotationLine.quotation_id == quotation.id
            )
        ).all()
        for line in existing_lines:
            session.delete(line)

        # Add new lines
        for line_data in quotation_in.quotation_lines:
            product = session.get(Product, line_data.product_id)
            if not product or product.organization_id != current_org.id:
                raise HTTPException(
                    status_code=404, detail=f"Product {line_data.product_id} not found"
                )
            line = QuotationLine(
                **line_data.model_dump(),
                quotation_id=quotation.id,
            )
            session.add(line)

    session.commit()
    session.refresh(quotation)

    # Load lines
    lines_statement = select(QuotationLine).where(
        QuotationLine.quotation_id == quotation.id
    )
    lines = session.exec(lines_statement).all()

    q_dict = quotation.model_dump()
    q_dict["contraagent_name"] = quotation.contraagent.name if quotation.contraagent else None
    q_dict["quotation_lines"] = [
        QuotationLinePublic.model_validate(line) for line in lines
    ]

    return QuotationPublic.model_validate(q_dict)


@router.delete("/{id}")
def delete_quotation(
    session: SessionDep,
    current_org: CurrentOrganization,
    membership: CurrentMembership,
    id: uuid.UUID,
) -> Message:
    """
    Delete a quotation. Requires manager role. Only draft quotations can be deleted.
    """
    if not has_role_or_higher(membership.role, OrganizationRole.MANAGER):
        raise HTTPException(status_code=403, detail="Requires manager role")

    quotation = session.get(Quotation, id)
    if not quotation:
        raise HTTPException(status_code=404, detail="Quotation not found")
    if quotation.organization_id != current_org.id:
        raise HTTPException(status_code=403, detail="Not enough permissions")

    # Check if quotation can be deleted (only draft status)
    if quotation.status != QuotationStatus.DRAFT:
        raise HTTPException(
            status_code=400, detail="Cannot delete quotation in current status"
        )

    # Delete lines first
    lines = session.exec(
        select(QuotationLine).where(
            QuotationLine.quotation_id == quotation.id
        )
    ).all()
    for line in lines:
        session.delete(line)

    session.delete(quotation)
    session.commit()
    return Message(message="Quotation deleted successfully")


@router.post("/{id}/send")
def send_quotation(
    session: SessionDep,
    current_org: CurrentOrganization,
    membership: CurrentMembership,
    id: uuid.UUID,
) -> Message:
    """
    Mark quotation as sent to contraagent.
    """
    quotation = session.get(Quotation, id)
    if not quotation:
        raise HTTPException(status_code=404, detail="Quotation not found")
    if quotation.organization_id != current_org.id:
        raise HTTPException(status_code=403, detail="Not enough permissions")

    if quotation.status != QuotationStatus.DRAFT:
        raise HTTPException(status_code=400, detail="Only draft quotations can be sent")

    quotation.status = QuotationStatus.SENT
    quotation.sent_date = utcnow()

    session.add(quotation)
    session.commit()

    return Message(message="Quotation sent successfully")


@router.post("/{id}/accept")
def accept_quotation(
    session: SessionDep,
    current_org: CurrentOrganization,
    membership: CurrentMembership,
    id: uuid.UUID,
) -> Message:
    """
    Mark quotation as accepted by contraagent.
    """
    quotation = session.get(Quotation, id)
    if not quotation:
        raise HTTPException(status_code=404, detail="Quotation not found")
    if quotation.organization_id != current_org.id:
        raise HTTPException(status_code=403, detail="Not enough permissions")

    if quotation.status not in [QuotationStatus.SENT, QuotationStatus.OPEN]:
        raise HTTPException(
            status_code=400, detail="Only sent or open quotations can be accepted"
        )

    quotation.status = QuotationStatus.ACCEPTED
    quotation.accepted_date = utcnow()

    session.add(quotation)
    session.commit()

    return Message(message="Quotation accepted successfully")


@router.post("/{id}/reject")
def reject_quotation(
    session: SessionDep,
    current_org: CurrentOrganization,
    membership: CurrentMembership,
    id: uuid.UUID,
    rejection_reason: str = Query(..., min_length=1),
) -> Message:
    """
    Mark quotation as rejected by contraagent.
    """
    quotation = session.get(Quotation, id)
    if not quotation:
        raise HTTPException(status_code=404, detail="Quotation not found")
    if quotation.organization_id != current_org.id:
        raise HTTPException(status_code=403, detail="Not enough permissions")

    if quotation.status not in [QuotationStatus.SENT, QuotationStatus.OPEN]:
        raise HTTPException(
            status_code=400, detail="Only sent or open quotations can be rejected"
        )

    quotation.status = QuotationStatus.REJECTED
    quotation.rejected_date = utcnow()
    quotation.rejection_reason = rejection_reason

    session.add(quotation)
    session.commit()

    return Message(message="Quotation rejected successfully")


@router.post("/{id}/cancel")
def cancel_quotation(
    session: SessionDep,
    current_org: CurrentOrganization,
    membership: CurrentMembership,
    id: uuid.UUID,
) -> Message:
    """
    Cancel a quotation. Requires manager role.
    """
    if not has_role_or_higher(membership.role, OrganizationRole.MANAGER):
        raise HTTPException(status_code=403, detail="Requires manager role")

    quotation = session.get(Quotation, id)
    if not quotation:
        raise HTTPException(status_code=404, detail="Quotation not found")
    if quotation.organization_id != current_org.id:
        raise HTTPException(status_code=403, detail="Not enough permissions")

    if quotation.status in [
        QuotationStatus.ACCEPTED,
        QuotationStatus.REJECTED,
        QuotationStatus.EXPIRED,
        QuotationStatus.CONVERTED_TO_INVOICE,
    ]:
        raise HTTPException(
            status_code=400, detail="Cannot cancel quotation in current status"
        )

    quotation.status = QuotationStatus.CANCELLED

    session.add(quotation)
    session.commit()

    return Message(message="Quotation cancelled successfully")


@router.post("/{id}/convert-to-invoice")
def convert_quotation_to_invoice(
    session: SessionDep,
    current_org: CurrentOrganization,
    membership: CurrentMembership,
    id: uuid.UUID,
) -> Message:
    """
    Convert quotation to invoice. Requires manager role.
    """
    if not has_role_or_higher(membership.role, OrganizationRole.MANAGER):
        raise HTTPException(status_code=403, detail="Requires manager role")

    quotation = session.get(Quotation, id)
    if not quotation:
        raise HTTPException(status_code=404, detail="Quotation not found")
    if quotation.organization_id != current_org.id:
        raise HTTPException(status_code=403, detail="Not enough permissions")

    if quotation.status != QuotationStatus.ACCEPTED:
        raise HTTPException(
            status_code=400,
            detail="Only accepted quotations can be converted to invoice",
        )

    # TODO: Create invoice from quotation data
    # This would create an invoice based on the quotation lines
    # For now, just mark the quotation as converted
    quotation.status = QuotationStatus.CONVERTED_TO_INVOICE

    session.add(quotation)
    session.commit()

    return Message(message="Quotation converted to invoice successfully")
