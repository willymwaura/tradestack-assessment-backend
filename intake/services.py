import hashlib
import json
from .models import Collection
from .models import CollectionAudit

def generate_batch_hash(payload):
    """
    Generate a deterministic hash for duplicate
    batch detection.
    """

    canonical_json = json.dumps(
        payload,
        sort_keys=True,
        default=str
    )

    return hashlib.sha256(
        canonical_json.encode("utf-8")
    ).hexdigest()




def process_receipt(receipt_data, batch):
    """
    Process a single receipt using
    last-write-wins semantics.
    """

    receipt_ref = receipt_data["receipt_ref"]

    existing = Collection.objects.filter(
        receipt_ref=receipt_ref
    ).first()

    payload_snapshot = {
        key: str(value)
        for key, value in receipt_data.items()
    }

    if not existing:

        collection = Collection.objects.create(
            receipt_ref=receipt_data["receipt_ref"],
            client_uuid=receipt_data["client_uuid"],
            outlet_code=receipt_data["outlet_code"],
            invoice_no=receipt_data["invoice_no"],
            method=receipt_data["method"],
            amount_kes=receipt_data["amount_kes"],
            recorded_at=receipt_data["recorded_at"],
            receipt_device_id=receipt_data.get(
                "device_id",
                ""
            ),
            batch=batch,
        )

        CollectionAudit.objects.create(
            collection=collection,
            action=CollectionAudit.Action.CREATED,
            payload=payload_snapshot,
        )

        return {
    "client_uuid": str(
        receipt_data["client_uuid"]
    ),
    "status": "created",
}

    if receipt_data["recorded_at"] > existing.recorded_at:

        existing.client_uuid = receipt_data["client_uuid"]
        existing.outlet_code = receipt_data["outlet_code"]
        existing.invoice_no = receipt_data["invoice_no"]
        existing.method = receipt_data["method"]
        existing.amount_kes = receipt_data["amount_kes"]
        existing.recorded_at = receipt_data["recorded_at"]
        existing.receipt_device_id = receipt_data.get(
            "device_id",
            ""
        )

        existing.batch = batch

        existing.save()

        CollectionAudit.objects.create(
            collection=existing,
            action=CollectionAudit.Action.UPDATED,
            payload=payload_snapshot,
        )

        return {
    "client_uuid": str(
        receipt_data["client_uuid"]
    ),
    "status": "updated",
}

    CollectionAudit.objects.create(
        collection=existing,
        action=CollectionAudit.Action.IGNORED_OLDER_VERSION,
        payload=payload_snapshot,
    )

    return {
    "client_uuid": str(
        receipt_data["client_uuid"]
    ),
    "status": "ignored",
}