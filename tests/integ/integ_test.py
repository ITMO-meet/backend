import pytest
import rollbar
from app import main
from app import setup_rollbar
import math

def test_main():
    res = main.main()
    assert res == "Hello, world!"

def test_rollbar():
    with pytest.raises(rollbar.ApiError) as e:
        setup_rollbar.main()
        assert e.value == "No token =/"
        
