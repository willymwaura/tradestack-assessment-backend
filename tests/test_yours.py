"""Your tests go here.

The acceptance tests cover the happy path the ticket describes. They do not
cover the cases the ticket left open. Those are the interesting ones, and we
will be looking for them.

`sample_batch.json` contains real captured traffic. Some of it is awkward.
"""

import pytest

URL = "/api/v1/collections/batch/"
LIST = "/api/v1/collections/"

def receipt(uuid, outlet, amount, ref, when="2026-07-14T11:42:08+03:00"):
    return {
        "client_uuid": uuid,
        "outlet_code": outlet,
        "invoice_no": "INV-480123",
        "method": "CASH",
        "amount_kes": amount,
        "receipt_ref": ref,
        "recorded_at": when,
    }

def test_batch_larger_than_200_receipts_is_rejected(
    client,
    outlets,
):
    code = outlets[0]["outlet_code"]

    receipts = []

    for i in range(201):
        receipts.append(
            {
                "client_uuid": f"11111111-0000-4000-8000-{i:012}",
                "outlet_code": code,
                "invoice_no": f"INV-{i}",
                "method": "CASH",
                "amount_kes": 100,
                "receipt_ref": f"RC{i}",
                "recorded_at": "2026-07-14T11:42:08+03:00",
            }
        )

    payload = {
        "device_id": "AND-KDG907X",
        "receipts": receipts,
    }

    response = client.post(
        URL,
        payload,
        format="json",
    )

    assert response.status_code == 400, response.content