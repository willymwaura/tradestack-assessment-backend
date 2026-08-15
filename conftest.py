import json
from pathlib import Path

import pytest

FIXTURES = Path(__file__).resolve().parent / "fixtures"


@pytest.fixture
def outlets(db):
    from intake.models import Outlet
    rows = json.loads((FIXTURES / "outlets.json").read_text())
    Outlet.objects.bulk_create(
        Outlet(outlet_code=r["outlet_code"], outlet_name=r["outlet_name"],
               route_code=r.get("route_code", "")) for r in rows)
    return rows


@pytest.fixture
def sample_batch():
    return json.loads((FIXTURES / "sample_batch.json").read_text())


@pytest.fixture
def client():
    from rest_framework.test import APIClient
    return APIClient()
