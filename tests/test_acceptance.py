"""Acceptance tests. These are the floor.

They must pass. They are not sufficient - we expect tests you wrote yourself
as well, especially around the parts of the contract the ticket did not
settle.

These tests deliberately assert on HTTP behaviour only. How you model and
store a receipt is your call.
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


@pytest.fixture
def three(outlets):
    code = outlets[0]["outlet_code"]
    return {
        "device_id": "AND-KDG907X",
        "receipts": [
            receipt("11111111-0000-4000-8000-000000000001", code, 14820.00, "RC100000001"),
            receipt("11111111-0000-4000-8000-000000000002", code, 3200.50, "RC100000002"),
            receipt("11111111-0000-4000-8000-000000000003", code, 990.00, "RC100000003"),
        ],
    }


def test_batch_is_accepted_and_persisted(client, three):
    r = client.post(URL, three, format="json")
    assert r.status_code in (200, 201, 207), r.content

    listed = client.get(LIST, {"outlet_code": three["receipts"][0]["outlet_code"]})
    assert listed.status_code == 200
    body = listed.json()
    results = body["results"] if isinstance(body, dict) else body
    assert len(results) == 3


def test_the_response_says_what_happened_to_each_receipt(client, three):
    """The depot needs to know the fate of every receipt, not just the batch.

    We do not prescribe the shape. We do require that all three client_uuids
    appear somewhere in the response body.
    """
    r = client.post(URL, three, format="json")
    body = r.content.decode()
    for item in three["receipts"]:
        assert item["client_uuid"] in body, f"{item['client_uuid']} not reported"


def test_a_replayed_batch_does_not_double_bank(client, three):
    """The handset retries the whole batch when it does not get a response."""
    first = client.post(URL, three, format="json")
    assert first.status_code in (200, 201, 207)
    second = client.post(URL, three, format="json")
    assert second.status_code in (200, 201, 207, 409)

    listed = client.get(LIST, {"outlet_code": three["receipts"][0]["outlet_code"]})
    body = listed.json()
    results = body["results"] if isinstance(body, dict) else body
    assert len(results) == 3, (
        f"replaying one batch produced {len(results)} receipts, expected 3"
    )
