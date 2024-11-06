import pytest
import rollbar

from app.main import app
from app import setup_rollbar
from fastapi.testclient import TestClient

client = TestClient(app)




def test_rollbar():
    with pytest.raises(rollbar.ApiError) as e:
        setup_rollbar.main()
        assert e.value == "No token =/"
