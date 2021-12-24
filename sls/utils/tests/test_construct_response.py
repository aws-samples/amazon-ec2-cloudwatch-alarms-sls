# pylint: disable=missing-module-docstring, missing-function-docstring

import unittest
import json

from unittest.mock import patch
from sls.utils.logger import Logger
from sls.utils.construct_response import ConstructResponse


class TestConstructResponse(unittest.TestCase):
    """
    Test for construct_response
    """

    def setUp(self):
        logger = Logger()
        logger.set_uuid("Context-id-testing")
        self.const_resp = ConstructResponse(logger)

    @patch("sls.utils.construct_response.ConstructResponse.get_response_headers")
    def test_construct_response(self, mock):
        mock.return_value = {
            "Content-Type": "application/json",
            "request-context-id": "testing"
        }
        code = 200
        key = "message"
        value = "testing"
        expected_return = {
            "statusCode": code,
            "headers": mock.return_value,
            "body": json.dumps({key: value})
        }
        actual_return = self.const_resp.construct_response(code, key, value)
        assert actual_return == expected_return

    @patch("sls.utils.construct_response.ConstructResponse.get_response_headers")
    def test_construct_error_response(self, mock):
        mock.return_value = {
            "Content-Type": "application/json",
            "request-context-id": "testing"
        }
        code = 404
        value = "testing_error"
        expected_return = {
            "statusCode": code,
            "headers": mock.return_value,
            "body": json.dumps({"error": value})
        }
        actual_return = self.const_resp.construct_error_response(code, value)
        assert actual_return == expected_return

    def test_get_response_headers(self):
        expected_return = {
            "Content-Type": "application/json",
            "request-context-id": "Context-id-testing"
        }
        actual_return = self.const_resp.get_response_headers()
        assert actual_return == expected_return
