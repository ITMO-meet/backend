import pytest
import rollbar
from unittest.mock import patch

from app import main, setup_rollbar


def test_main():
    res = main.main()
    assert res == "Hello, world!"


def test_rollbar_init():
    with patch("app.setup_rollbar.rollbar.init") as mock_init:
        setup_rollbar.init_rollbar()
        mock_init.assert_called_once()


def test_rollbar_error_handling():
    @setup_rollbar.rollbar_handler
    def error_function():
        raise rollbar.ApiError("No token =/")

    with patch("app.setup_rollbar.rollbar.report_exc_info") as mock_report:
        with pytest.raises(rollbar.ApiError, match="No token =/"):
            error_function()
        mock_report.assert_called_once()
