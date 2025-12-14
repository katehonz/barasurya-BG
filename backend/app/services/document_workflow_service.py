"""
Document workflow service - управление на статусите и преходите на документи.
"""

import uuid
from datetime import datetime
from typing import Dict, List, Optional, Type, Any
from enum import Enum

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update

from app.models.invoice import Invoice, InvoiceStatus
from app.models.purchase_order import PurchaseOrder, PurchaseOrderStatus
from app.models.quotation import Quotation, QuotationStatus
from app.utils import utcnow


class WorkflowTransition:
    """Represents a workflow transition."""

    def __init__(
        self,
        from_status: str,
        to_status: str,
        action_name: str,
        requires_permission: Optional[str] = None,
        auto_timestamp_field: Optional[str] = None,
        validation_rules: Optional[List[callable]] = None,
    ):
        self.from_status = from_status
        self.to_status = to_status
        self.action_name = action_name
        self.requires_permission = requires_permission
        self.auto_timestamp_field = auto_timestamp_field
        self.validation_rules = validation_rules or []


class DocumentWorkflowService:
    """Service for managing document workflows and status transitions."""

    # Invoice workflow transitions
    INVOICE_WORKFLOW = {
        InvoiceStatus.DRAFT: [
            WorkflowTransition(
                from_status=InvoiceStatus.DRAFT,
                to_status=InvoiceStatus.ISSUED,
                action_name="issue",
                requires_permission="invoice.issue",
                auto_timestamp_field="date_issued",
            ),
            WorkflowTransition(
                from_status=InvoiceStatus.DRAFT,
                to_status=InvoiceStatus.CANCELLED,
                action_name="cancel",
                requires_permission="invoice.cancel",
            ),
        ],
        InvoiceStatus.ISSUED: [
            WorkflowTransition(
                from_status=InvoiceStatus.ISSUED,
                to_status=InvoiceStatus.PARTIALLY_PAID,
                action_name="partial_payment",
                requires_permission="payment.create",
            ),
            WorkflowTransition(
                from_status=InvoiceStatus.ISSUED,
                to_status=InvoiceStatus.PAID,
                action_name="pay",
                requires_permission="payment.create",
                auto_timestamp_field="date_paid",
            ),
            WorkflowTransition(
                from_status=InvoiceStatus.ISSUED,
                to_status=InvoiceStatus.OVERDUE,
                action_name="mark_overdue",
                requires_permission="invoice.update",
            ),
            WorkflowTransition(
                from_status=InvoiceStatus.ISSUED,
                to_status=InvoiceStatus.CANCELLED,
                action_name="cancel",
                requires_permission="invoice.cancel",
            ),
        ],
        InvoiceStatus.PARTIALLY_PAID: [
            WorkflowTransition(
                from_status=InvoiceStatus.PARTIALLY_PAID,
                to_status=InvoiceStatus.PAID,
                action_name="pay",
                requires_permission="payment.create",
                auto_timestamp_field="date_paid",
            ),
            WorkflowTransition(
                from_status=InvoiceStatus.PARTIALLY_PAID,
                to_status=InvoiceStatus.OVERDUE,
                action_name="mark_overdue",
                requires_permission="invoice.update",
            ),
        ],
        InvoiceStatus.OVERDUE: [
            WorkflowTransition(
                from_status=InvoiceStatus.OVERDUE,
                to_status=InvoiceStatus.PARTIALLY_PAID,
                action_name="partial_payment",
                requires_permission="payment.create",
            ),
            WorkflowTransition(
                from_status=InvoiceStatus.OVERDUE,
                to_status=InvoiceStatus.PAID,
                action_name="pay",
                requires_permission="payment.create",
                auto_timestamp_field="date_paid",
            ),
        ],
    }

    # Purchase Order workflow transitions
    PURCHASE_ORDER_WORKFLOW = {
        PurchaseOrderStatus.DRAFT: [
            WorkflowTransition(
                from_status=PurchaseOrderStatus.DRAFT,
                to_status=PurchaseOrderStatus.SENT,
                action_name="send",
                requires_permission="purchase_order.send",
                auto_timestamp_field="sent_date",
            ),
            WorkflowTransition(
                from_status=PurchaseOrderStatus.DRAFT,
                to_status=PurchaseOrderStatus.CANCELLED,
                action_name="cancel",
                requires_permission="purchase_order.cancel",
            ),
        ],
        PurchaseOrderStatus.SENT: [
            WorkflowTransition(
                from_status=PurchaseOrderStatus.SENT,
                to_status=PurchaseOrderStatus.CONFIRMED,
                action_name="confirm",
                requires_permission="purchase_order.confirm",
                auto_timestamp_field="confirmed_date",
            ),
            WorkflowTransition(
                from_status=PurchaseOrderStatus.SENT,
                to_status=PurchaseOrderStatus.CANCELLED,
                action_name="cancel",
                requires_permission="purchase_order.cancel",
            ),
        ],
        PurchaseOrderStatus.CONFIRMED: [
            WorkflowTransition(
                from_status=PurchaseOrderStatus.CONFIRMED,
                to_status=PurchaseOrderStatus.PARTIALLY_RECEIVED,
                action_name="partial_receive",
                requires_permission="purchase_order.receive",
            ),
            WorkflowTransition(
                from_status=PurchaseOrderStatus.CONFIRMED,
                to_status=PurchaseOrderStatus.RECEIVED,
                action_name="receive",
                requires_permission="purchase_order.receive",
                auto_timestamp_field="received_date",
            ),
            WorkflowTransition(
                from_status=PurchaseOrderStatus.CONFIRMED,
                to_status=PurchaseOrderStatus.CANCELLED,
                action_name="cancel",
                requires_permission="purchase_order.cancel",
            ),
        ],
        PurchaseOrderStatus.PARTIALLY_RECEIVED: [
            WorkflowTransition(
                from_status=PurchaseOrderStatus.PARTIALLY_RECEIVED,
                to_status=PurchaseOrderStatus.RECEIVED,
                action_name="receive",
                requires_permission="purchase_order.receive",
                auto_timestamp_field="received_date",
            ),
        ],
        PurchaseOrderStatus.RECEIVED: [
            WorkflowTransition(
                from_status=PurchaseOrderStatus.RECEIVED,
                to_status=PurchaseOrderStatus.CLOSED,
                action_name="close",
                requires_permission="purchase_order.close",
            ),
        ],
    }

    # Quotation workflow transitions
    QUOTATION_WORKFLOW = {
        QuotationStatus.DRAFT: [
            WorkflowTransition(
                from_status=QuotationStatus.DRAFT,
                to_status=QuotationStatus.SENT,
                action_name="send",
                requires_permission="quotation.send",
                auto_timestamp_field="sent_date",
            ),
            WorkflowTransition(
                from_status=QuotationStatus.DRAFT,
                to_status=QuotationStatus.CANCELLED,
                action_name="cancel",
                requires_permission="quotation.cancel",
            ),
        ],
        QuotationStatus.SENT: [
            WorkflowTransition(
                from_status=QuotationStatus.SENT,
                to_status=QuotationStatus.OPEN,
                action_name="open",
                requires_permission="quotation.update",
            ),
            WorkflowTransition(
                from_status=QuotationStatus.SENT,
                to_status=QuotationStatus.ACCEPTED,
                action_name="accept",
                requires_permission="quotation.accept",
                auto_timestamp_field="accepted_date",
            ),
            WorkflowTransition(
                from_status=QuotationStatus.SENT,
                to_status=QuotationStatus.REJECTED,
                action_name="reject",
                requires_permission="quotation.reject",
                auto_timestamp_field="rejected_date",
            ),
            WorkflowTransition(
                from_status=QuotationStatus.SENT,
                to_status=QuotationStatus.EXPIRED,
                action_name="expire",
                requires_permission="quotation.update",
            ),
        ],
        QuotationStatus.OPEN: [
            WorkflowTransition(
                from_status=QuotationStatus.OPEN,
                to_status=QuotationStatus.ACCEPTED,
                action_name="accept",
                requires_permission="quotation.accept",
                auto_timestamp_field="accepted_date",
            ),
            WorkflowTransition(
                from_status=QuotationStatus.OPEN,
                to_status=QuotationStatus.REJECTED,
                action_name="reject",
                requires_permission="quotation.reject",
                auto_timestamp_field="rejected_date",
            ),
            WorkflowTransition(
                from_status=QuotationStatus.OPEN,
                to_status=QuotationStatus.EXPIRED,
                action_name="expire",
                requires_permission="quotation.update",
            ),
        ],
        QuotationStatus.ACCEPTED: [
            WorkflowTransition(
                from_status=QuotationStatus.ACCEPTED,
                to_status=QuotationStatus.CONVERTED_TO_INVOICE,
                action_name="convert_to_invoice",
                requires_permission="quotation.convert",
            ),
        ],
    }

    @staticmethod
    def get_available_transitions(
        document_type: str, current_status: str
    ) -> List[WorkflowTransition]:
        """Get available transitions for a document type and current status."""
        workflows = {
            "invoice": DocumentWorkflowService.INVOICE_WORKFLOW,
            "purchase_order": DocumentWorkflowService.PURCHASE_ORDER_WORKFLOW,
            "quotation": DocumentWorkflowService.QUOTATION_WORKFLOW,
        }

        workflow = workflows.get(document_type, {})
        return workflow.get(current_status, [])

    @staticmethod
    def can_transition(
        document_type: str,
        current_status: str,
        target_status: str,
        user_permissions: List[str],
    ) -> bool:
        """Check if a transition is allowed."""
        transitions = DocumentWorkflowService.get_available_transitions(
            document_type, current_status
        )

        for transition in transitions:
            if transition.to_status == target_status:
                if transition.requires_permission:
                    return transition.requires_permission in user_permissions
                return True

        return False

    @staticmethod
    async def execute_transition(
        db: AsyncSession,
        document_type: str,
        document_id: uuid.UUID,
        target_status: str,
        user_id: uuid.UUID,
        user_permissions: List[str],
        additional_data: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Execute a document status transition.

        Args:
            db: Database session
            document_type: Type of document (invoice, purchase_order, quotation)
            document_id: Document UUID
            target_status: Target status
            user_id: User UUID executing the transition
            user_permissions: List of user permissions
            additional_data: Additional data for the transition

        Returns:
            Dictionary with transition result
        """
        # Get document model class
        model_classes = {
            "invoice": Invoice,
            "purchase_order": PurchaseOrder,
            "quotation": Quotation,
        }

        model_class = model_classes.get(document_type)
        if not model_class:
            raise ValueError(f"Unknown document type: {document_type}")

        # Get current document
        stmt = select(model_class).where(model_class.id == document_id)
        result = await db.execute(stmt)
        document = result.scalar_one_or_none()

        if not document:
            raise ValueError(f"Document not found: {document_id}")

        current_status = document.status

        # Check if transition is allowed
        if not DocumentWorkflowService.can_transition(
            document_type, current_status, target_status, user_permissions
        ):
            raise ValueError(
                f"Transition from {current_status} to {target_status} not allowed"
            )

        # Get transition details
        transitions = DocumentWorkflowService.get_available_transitions(
            document_type, current_status
        )
        transition = None
        for t in transitions:
            if t.to_status == target_status:
                transition = t
                break

        if not transition:
            raise ValueError(
                f"Transition from {current_status} to {target_status} not found"
            )

        # Execute validation rules
        if transition.validation_rules:
            for rule in transition.validation_rules:
                if not rule(document, additional_data):
                    raise ValueError(
                        f"Validation failed for transition {transition.action_name}"
                    )

        # Update document status
        update_data = {"status": target_status}

        # Add auto timestamp
        if transition.auto_timestamp_field:
            update_data[transition.auto_timestamp_field] = utcnow()

        # Add additional data
        if additional_data:
            update_data.update(additional_data)

        # Update document
        stmt = (
            update(model_class)
            .where(model_class.id == document_id)
            .values(**update_data)
        )
        await db.execute(stmt)
        await db.commit()

        return {
            "success": True,
            "document_id": document_id,
            "document_type": document_type,
            "from_status": current_status,
            "to_status": target_status,
            "action": transition.action_name,
            "timestamp": utcnow(),
            "updated_fields": list(update_data.keys()),
        }

    @staticmethod
    def get_workflow_diagram(document_type: str) -> Dict[str, List[str]]:
        """Get workflow diagram for a document type."""
        workflows = {
            "invoice": DocumentWorkflowService.INVOICE_WORKFLOW,
            "purchase_order": DocumentWorkflowService.PURCHASE_ORDER_WORKFLOW,
            "quotation": DocumentWorkflowService.QUOTATION_WORKFLOW,
        }

        workflow = workflows.get(document_type, {})
        diagram = {}

        for status, transitions in workflow.items():
            diagram[status.value] = [t.to_status.value for t in transitions]

        return diagram


# Common validation rules
def validate_invoice_not_paid(
    document: Invoice, additional_data: Optional[Dict] = None
) -> bool:
    """Validate that invoice is not already paid."""
    return document.status != InvoiceStatus.PAID


def validate_purchase_order_has_lines(
    document: PurchaseOrder, additional_data: Optional[Dict] = None
) -> bool:
    """Validate that purchase order has lines before sending."""
    # This would need to check if there are lines
    return True


def validate_quotation_valid_until(
    document: Quotation, additional_data: Optional[Dict] = None
) -> bool:
    """Validate that quotation is not expired."""
    if not document.valid_until:
        return True
    return document.valid_until >= datetime.now().date()
