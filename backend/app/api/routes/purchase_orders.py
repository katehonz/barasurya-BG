"""
Purchase Order API endpoints - управление на поръчки за доставка.
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
from app.models.purchase_order import (
    PurchaseOrder,
    PurchaseOrderCreate,
    PurchaseOrderPublic,
    PurchaseOrderUpdate,
    PurchaseOrdersPublic,
    PurchaseOrderStatus,
    PurchaseOrderPriority,
)
from app.models.purchase_order_line import (
    PurchaseOrderLine,
    PurchaseOrderLineCreate,
    PurchaseOrderLinePublic,
)
from app.models.contraagent import Contraagent
from app.models.warehouse import Warehouse
from app.models.product import Product
from app.services.document_numbering_service import (
    DocumentNumberingService,
    DocumentUIDService,
)
from app.utils import utcnow

router = APIRouter(prefix="/purchase-orders", tags=["purchase-orders"])


@router.get("/", response_model=PurchaseOrdersPublic)
def read_purchase_orders(
    session: SessionDep,
    current_org: CurrentOrganization,
    membership: CurrentMembership,
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=100, ge=0, le=100),
    status: PurchaseOrderStatus | None = Query(default=None),
    contraagent_id: uuid.UUID | None = Query(default=None),
) -> Any:
    """
    Retrieve purchase orders for the current organization.
    """
    count_statement = (
        select(func.count())
        .select_from(PurchaseOrder)
        .where(PurchaseOrder.organization_id == current_org.id)
    )
    if status:
        count_statement = count_statement.where(PurchaseOrder.status == status)
    if contraagent_id:
        count_statement = count_statement.where(PurchaseOrder.contraagent_id == contraagent_id)
    count = session.exec(count_statement).one()

    statement = (
        select(PurchaseOrder)
        .options(selectinload(PurchaseOrder.contraagent)) # Changed from supplier
        .where(PurchaseOrder.organization_id == current_org.id)
    )
    if status:
        statement = statement.where(PurchaseOrder.status == status)
    if contraagent_id:
        statement = statement.where(PurchaseOrder.contraagent_id == contraagent_id)
    statement = statement.offset(skip).limit(limit).order_by(PurchaseOrder.date_created.desc())
    purchase_orders = session.exec(statement).all()

    # Convert to public schemas with related data
    purchase_orders_public = []
    for po in purchase_orders:
        # Load related lines
        lines_statement = select(PurchaseOrderLine).where(
            PurchaseOrderLine.purchase_order_id == po.id
        )
        lines = session.exec(lines_statement).all()

        po_dict = po.model_dump()
        po_dict["contraagent_name"] = po.contraagent.name if po.contraagent else None # Changed from supplier_name and po.supplier
        po_dict["warehouse_name"] = None  # Warehouse relationship disabled
        po_dict["purchase_order_lines"] = [
            PurchaseOrderLinePublic.model_validate(line) for line in lines
        ]
        purchase_orders_public.append(PurchaseOrderPublic.model_validate(po_dict))

    return PurchaseOrdersPublic(data=purchase_orders_public, count=count)


@router.get("/{id}", response_model=PurchaseOrderPublic)
def read_purchase_order(
    session: SessionDep,
    current_org: CurrentOrganization,
    membership: CurrentMembership,
    id: uuid.UUID,
) -> Any:
    """
    Get purchase order by ID.
    """
    purchase_order = session.get(PurchaseOrder, id)
    if not purchase_order:
        raise HTTPException(status_code=404, detail="Purchase order not found")
    if purchase_order.organization_id != current_org.id:
        raise HTTPException(status_code=403, detail="Not enough permissions")

    po_dict = purchase_order.model_dump()
    po_dict["contraagent_name"] = purchase_order.contraagent.name if purchase_order.contraagent else None # Changed from supplier_name and purchase_order.supplier
    po_dict["warehouse_name"] = None  # Warehouse relationship disabled
    po_dict["purchase_order_lines"] = [
        PurchaseOrderLinePublic.model_validate(line) for line in lines
    ]

    return PurchaseOrderPublic.model_validate(po_dict)


@router.post("/", response_model=PurchaseOrderPublic)
def create_purchase_order(
    *,
    session: SessionDep,
    current_user: CurrentUser,
    current_org: CurrentOrganization,
    membership: CurrentMembership,
    purchase_order_in: PurchaseOrderCreate,
) -> Any:
    """
    Create new purchase order. Requires at least member role.
    """
    # Validate contraagent exists and belongs to organization
    contraagent = session.get(Contraagent, purchase_order_in.contraagent_id)
    if not contraagent or contraagent.organization_id != current_org.id:
        raise HTTPException(status_code=404, detail="Contraagent not found")
    if not contraagent.is_supplier: # Check if contraagent is a supplier
        raise HTTPException(status_code=403, detail="Contraagent is not a supplier")

    # Note: warehouse validation disabled - table doesn't exist yet
    # if purchase_order_in.warehouse_id:
    #     warehouse = session.get(Warehouse, purchase_order_in.warehouse_id)
    #     if not warehouse or warehouse.organization_id != current_org.id:
    #         raise HTTPException(status_code=404, detail="Warehouse not found")

    # Validate products
    for line in purchase_order_in.purchase_order_lines:
        product = session.get(Product, line.product_id)
        if not product or product.organization_id != current_org.id:
            raise HTTPException(
                status_code=404, detail=f"Product {line.product_id} not found"
            )

    # Generate order number
    order_no = f"PO{current_org.purchase_order_next_number:010d}"
    document_uid = DocumentUIDService.generate_document_uid(
        "purchase_order", current_org.id, order_no
    )

    # Update next number
    current_org.purchase_order_next_number += 1
    session.add(current_org)

    # Create purchase order
    po_data = purchase_order_in.model_dump(exclude={"purchase_order_lines"})
    purchase_order = PurchaseOrder(
        **po_data,
        order_no=order_no,
        document_uid=document_uid,
        organization_id=current_org.id,
        created_by_id=current_user.id,
    )
    session.add(purchase_order)
    session.flush()  # Get the ID

    # Create lines
    lines = []
    for line_data in purchase_order_in.purchase_order_lines:
        line = PurchaseOrderLine(
            **line_data.model_dump(),
            purchase_order_id=purchase_order.id,
            remaining_quantity=line_data.quantity,
        )
        session.add(line)
        lines.append(line)

    session.commit()
    session.refresh(purchase_order)

    po_dict = purchase_order.model_dump()
    po_dict["contraagent_name"] = contraagent.name # Changed from supplier.name
    po_dict["warehouse_name"] = None  # Warehouse table doesn't exist yet
    po_dict["purchase_order_lines"] = [
        PurchaseOrderLinePublic.model_validate(line) for line in lines
    ]

    return PurchaseOrderPublic.model_validate(po_dict)


@router.put("/{id}", response_model=PurchaseOrderPublic)
def update_purchase_order(
    *,
    session: SessionDep,
    current_org: CurrentOrganization,
    membership: CurrentMembership,
    id: uuid.UUID,
    purchase_order_in: PurchaseOrderUpdate,
) -> Any:
    """
    Update a purchase order. Requires at least manager role.
    """
    if not has_role_or_higher(membership.role, OrganizationRole.MANAGER):
        raise HTTPException(status_code=403, detail="Requires manager role")

    purchase_order = session.get(PurchaseOrder, id)
    if not purchase_order:
        raise HTTPException(status_code=404, detail="Purchase order not found")
    if purchase_order.organization_id != current_org.id:
        raise HTTPException(status_code=403, detail="Not enough permissions")

    # Check if order can be updated (not in final status)
    if purchase_order.status in [
        PurchaseOrderStatus.RECEIVED,
        PurchaseOrderStatus.CANCELLED,
        PurchaseOrderStatus.CLOSED,
    ]:
        raise HTTPException(
            status_code=400, detail="Cannot update purchase order in current status"
        )

    # Note: warehouse validation disabled - table doesn't exist yet
    # if purchase_order_in.warehouse_id:
    #     warehouse = session.get(Warehouse, purchase_order_in.warehouse_id)
    #     if not warehouse or warehouse.organization_id != current_org.id:
    #         raise HTTPException(status_code=404, detail="Warehouse not found")

    if purchase_order_in.contraagent_id is not None: # Changed from supplier_id
        contraagent = session.get(Contraagent, purchase_order_in.contraagent_id) # Changed from supplier
        if not contraagent or contraagent.organization_id != current_org.id:
            raise HTTPException(status_code=404, detail="Contraagent not found")
        if not contraagent.is_supplier: # Check if contraagent is a supplier
            raise HTTPException(status_code=403, detail="Contraagent is not a supplier")

    # Update main object
    update_dict = purchase_order_in.model_dump(exclude_unset=True, exclude={"purchase_order_lines"})
    update_dict.update(BaseModelUpdate().model_dump())
    purchase_order.sqlmodel_update(update_dict)
    session.add(purchase_order)

    # Update lines if provided
    if purchase_order_in.purchase_order_lines is not None:
        # Delete existing lines
        existing_lines = session.exec(
            select(PurchaseOrderLine).where(
                PurchaseOrderLine.purchase_order_id == purchase_order.id
            )
        ).all()
        for line in existing_lines:
            session.delete(line)

        # Add new lines
        for line_data in purchase_order_in.purchase_order_lines:
            product = session.get(Product, line_data.product_id)
            if not product or product.organization_id != current_org.id:
                raise HTTPException(
                    status_code=404, detail=f"Product {line_data.product_id} not found"
                )
            line = PurchaseOrderLine(
                **line_data.model_dump(),
                purchase_order_id=purchase_order.id,
                remaining_quantity=line_data.quantity,
            )
            session.add(line)

    session.commit()
    session.refresh(purchase_order)

    # Load lines
    lines_statement = select(PurchaseOrderLine).where(
        PurchaseOrderLine.purchase_order_id == purchase_order.id
    )
    lines = session.exec(lines_statement).all()

    po_dict = purchase_order.model_dump()
    po_dict["contraagent_name"] = purchase_order.contraagent.name if purchase_order.contraagent else None # Changed from supplier_name and purchase_order.supplier
    po_dict["warehouse_name"] = None  # Warehouse relationship disabled
    po_dict["purchase_order_lines"] = [
        PurchaseOrderLinePublic.model_validate(line) for line in lines
    ]

    return PurchaseOrderPublic.model_validate(po_dict)


@router.delete("/{id}")
def delete_purchase_order(
    session: SessionDep,
    current_org: CurrentOrganization,
    membership: CurrentMembership,
    id: uuid.UUID,
) -> Message:
    """
    Delete a purchase order. Requires manager role. Only draft orders can be deleted.
    """
    if not has_role_or_higher(membership.role, OrganizationRole.MANAGER):
        raise HTTPException(status_code=403, detail="Requires manager role")

    purchase_order = session.get(PurchaseOrder, id)
    if not purchase_order:
        raise HTTPException(status_code=404, detail="Purchase order not found")
    if purchase_order.organization_id != current_org.id:
        raise HTTPException(status_code=403, detail="Not enough permissions")

    # Check if order can be deleted (only draft status)
    if purchase_order.status != PurchaseOrderStatus.DRAFT:
        raise HTTPException(
            status_code=400, detail="Cannot delete purchase order in current status"
        )

    # Delete lines first
    lines = session.exec(
        select(PurchaseOrderLine).where(
            PurchaseOrderLine.purchase_order_id == purchase_order.id
        )
    ).all()
    for line in lines:
        session.delete(line)

    session.delete(purchase_order)
    session.commit()
    return Message(message="Purchase order deleted successfully")


@router.post("/{id}/send")
def send_purchase_order(
    session: SessionDep,
    current_org: CurrentOrganization,
    membership: CurrentMembership,
    id: uuid.UUID,
) -> Message:
    """
    Mark purchase order as sent to contraagent.
    """
    purchase_order = session.get(PurchaseOrder, id)
    if not purchase_order:
        raise HTTPException(status_code=404, detail="Purchase order not found")
    if purchase_order.organization_id != current_org.id:
        raise HTTPException(status_code=403, detail="Not enough permissions")

    if purchase_order.status != PurchaseOrderStatus.DRAFT:
        raise HTTPException(status_code=400, detail="Only draft orders can be sent")

    purchase_order.status = PurchaseOrderStatus.SENT
    purchase_order.sent_date = utcnow()

    session.add(purchase_order)
    session.commit()

    return Message(message="Purchase order sent successfully")


@router.post("/{id}/confirm")
def confirm_purchase_order(
    session: SessionDep,
    current_org: CurrentOrganization,
    membership: CurrentMembership,
    id: uuid.UUID,
) -> Message:
    """
    Mark purchase order as confirmed by contraagent.
    """
    purchase_order = session.get(PurchaseOrder, id)
    if not purchase_order:
        raise HTTPException(status_code=404, detail="Purchase order not found")
    if purchase_order.organization_id != current_org.id:
        raise HTTPException(status_code=403, detail="Not enough permissions")

    if purchase_order.status != PurchaseOrderStatus.SENT:
        raise HTTPException(status_code=400, detail="Only sent orders can be confirmed")

    purchase_order.status = PurchaseOrderStatus.CONFIRMED
    purchase_order.confirmed_date = utcnow()

    session.add(purchase_order)
    session.commit()

    return Message(message="Purchase order confirmed successfully")


@router.post("/{id}/cancel")
def cancel_purchase_order(
    session: SessionDep,
    current_org: CurrentOrganization,
    membership: CurrentMembership,
    id: uuid.UUID,
) -> Message:
    """
    Cancel a purchase order. Requires manager role.
    """
    if not has_role_or_higher(membership.role, OrganizationRole.MANAGER):
        raise HTTPException(status_code=403, detail="Requires manager role")

    purchase_order = session.get(PurchaseOrder, id)
    if not purchase_order:
        raise HTTPException(status_code=404, detail="Purchase order not found")
    if purchase_order.organization_id != current_org.id:
        raise HTTPException(status_code=403, detail="Not enough permissions")

    if purchase_order.status in [
        PurchaseOrderStatus.RECEIVED,
        PurchaseOrderStatus.CLOSED,
        PurchaseOrderStatus.CANCELLED,
    ]:
        raise HTTPException(
            status_code=400, detail="Cannot cancel purchase order in current status"
        )

    purchase_order.status = PurchaseOrderStatus.CANCELLED

    session.add(purchase_order)
    session.commit()

    return Message(message="Purchase order cancelled successfully")
