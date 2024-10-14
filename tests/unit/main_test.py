import pytest
import rollbar
from app import main
from app import setup_rollbar

def test_main():
    res = main.main()
    assert res == "Hello, world!"

def test_rollbar():
    with pytest.raises(rollbar.ApiError) as e:
        setup_rollbar.main()
        assert e.value == "No token =/"
        
def test_bad():
    assert 2 + 2 == 5 # OMG 1984 reference!!!
        
