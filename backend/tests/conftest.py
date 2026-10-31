import os
import sys

# Must be set before `config` is imported: force CSV fallback, no startup warm-up.
os.environ["VOLGUARD_OFFLINE"] = "1"
os.environ["VOLGUARD_WARMUP"] = "0"
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pytest
from fastapi.testclient import TestClient


@pytest.fixture(scope="session")
def client():
    import api
    with TestClient(api.app) as c:
        yield c
