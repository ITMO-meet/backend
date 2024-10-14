from app import main

def test_sdds():
    res = main.main()
    assert res == "Hello, world!"
