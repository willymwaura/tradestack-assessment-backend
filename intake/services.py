import hashlib
import json


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

