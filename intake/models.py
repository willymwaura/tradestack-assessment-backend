"""Models for collection intake.

`Outlet` is given to you, complete, and is seeded by `make seed`.

Everything else is yours. There is deliberately no receipt model here - how
you store a receipt, what you make unique, and what you index are decisions we
want to see you make. Write down the reasoning in DECISIONS.md.
"""
from django.db import models


class Outlet(models.Model):
    outlet_code = models.CharField(max_length=16, primary_key=True)
    outlet_name = models.CharField(max_length=120)
    route_code = models.CharField(max_length=16, blank=True)

    class Meta:
        ordering = ["outlet_code"]

    def __str__(self):
        return f"{self.outlet_code} {self.outlet_name}"

from django.db import models





class CollectionBatch(models.Model):
    """
    Tracks uploaded batches and supports
    duplicate batch detection.
    """

    device_id = models.CharField(max_length=50)

    batch_hash = models.CharField(
        max_length=64,
        unique=True
    )

    receipt_count = models.PositiveIntegerField()

    received_at = models.DateTimeField(
        auto_now_add=True
    )

    class Meta:
        ordering = ["-received_at"]

    def __str__(self):
        return f"{self.device_id} ({self.receipt_count})"


class Collection(models.Model):
    """
    Current state of a receipt.
    Last-write-wins updates this record.
    """

    METHOD_CHOICES = (
        ("CASH", "Cash"),
        ("MPESA", "M-Pesa"),
        ("CHEQUE", "Cheque"),
    )

    receipt_ref = models.CharField(
        max_length=50,
        unique=True
    )

    client_uuid = models.UUIDField()

    outlet_code = models.CharField(
    max_length=16,
    db_index=True,
    default="ZX"
)

    invoice_no = models.CharField(
        max_length=50
    )

    method = models.CharField(
        max_length=20,
        choices=METHOD_CHOICES
    )

    amount_kes = models.DecimalField(
        max_digits=12,
        decimal_places=2
    )

    recorded_at = models.DateTimeField()

    receipt_device_id = models.CharField(
        max_length=50,
        blank=True
    )

    batch = models.ForeignKey(
        CollectionBatch,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="collections"
    )

    received_at = models.DateTimeField(
        auto_now_add=True
    )

    updated_at = models.DateTimeField(
        auto_now=True
    )

    class Meta:
        ordering = ["-recorded_at"]
        indexes = [
            models.Index(fields=["recorded_at"]),
            models.Index(fields=["outlet_code"]),
        ]

    def __str__(self):
        return self.receipt_ref


class CollectionAudit(models.Model):
    """
    Audit trail for collection processing.
    Stores every accepted or ignored event.
    """

    class Action(models.TextChoices):
        CREATED = "CREATED", "Created"
        UPDATED = "UPDATED", "Updated"
        IGNORED_OLDER_VERSION = (
            "IGNORED_OLDER_VERSION",
            "Ignored Older Version",
        )

    collection = models.ForeignKey(
        Collection,
        on_delete=models.CASCADE,
        related_name="audit_logs"
    )

    action = models.CharField(
        max_length=50,
        choices=Action.choices
    )

    payload = models.JSONField()

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.collection.receipt_ref} - {self.action}"


class BatchAudit(models.Model):
    """
    Audit trail for batch processing.
    """

    class Action(models.TextChoices):
        PROCESSED = "PROCESSED", "Processed"
        DUPLICATE_BATCH = "DUPLICATE_BATCH", "Duplicate Batch"

    batch = models.ForeignKey(
        CollectionBatch,
        on_delete=models.CASCADE,
        related_name="audit_logs"
    )

    action = models.CharField(
        max_length=50,
        choices=Action.choices
    )

    details = models.JSONField(
        default=dict,
        blank=True
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.batch.id} - {self.action}"
