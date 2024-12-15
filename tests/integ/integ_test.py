from unittest.mock import patch

from app import main, setup_rollbar


def test_main():
    res = main.main()
    assert res == "Hello, world!"


def test_rollbar_init():
    with patch("app.setup_rollbar.rollbar.init") as mock_init:
        setup_rollbar.init_rollbar()
        mock_init.assert_called_once()


