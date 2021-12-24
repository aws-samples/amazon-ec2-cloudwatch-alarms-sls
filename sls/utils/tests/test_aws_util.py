# pylint: disable=unused-argument,protected-access,arguments-differ,no-name-in-module,import-error,wrong-import-position, missing-module-docstring, missing-function-docstring, missing-class-docstring
import os
import unittest

from unittest.mock import patch
import os, sys
module_dir = os.path.dirname(os.path.abspath(__file__))
module_par = os.path.normpath(os.path.join(module_dir, '../../../'))
sys.path.append(module_par)
from sls.utils.api_request import ApiRequests
from sls.utils.aws_creds import AwsCreds
from sls.utils.aws_sm import SmClient

os.environ["token_url"] = "mock"
os.environ["token_url"] = "mock"
os.environ["rds_metadata_api_client_id"] = "mock"
os.environ["LDAP_PASSWORD_SECRET_NAME"] = "mock"

os.environ["vpcxiam_endpoint"] = "mock"
os.environ["vpcxiam_scope"] = "mock"
os.environ["vpcxiam_host"] = "mock"


class TestUtilities(unittest.TestCase):

    # Tests for api_request.py
    @patch("sls.utils.api_request.get_secret_value", return_value="")
    #@patch("sls.utils.api_request.get_bearer_token")
    @patch("sls.utils.api_request.req")
    def test_request(self, mock_req, mock_secret):
        """
        test_request: Test REST request
        """
        expected_resp = type("Response", (object,), dict(status_code=200))
        #mock.return_value = "Bearer xxxxx"
        mock_req.return_value = expected_resp
        api_request = ApiRequests()
        response = api_request.request("url", "get")
        self.assertEqual(response.status_code, 200)

    #@patch("sls.utils.api_request.get_bearer_token")
    @patch("sls.utils.api_request.get_secret_value", return_value="")
    @patch("sls.utils.api_request.req")
    def test_request_exception(self, mock_req, mock_secret):
        """
        test_request_exception
        """
        expected_resp = type("Response", (object,), dict(status_code=300, content="Test exception"))
        #mock.return_value = "Bearer xxxxx"
        mock_req.return_value = expected_resp
        api_request = ApiRequests()
        self.assertRaises(Exception, api_request.request, "url", "get")

    #@patch("sls.utils.api_request.get_bearer_token")
    @patch("sls.utils.api_request.get_secret_value", return_value="")
    def test_token_exception(self, mock):
        """
        test_token_exception
        """
        mock.side_effect = Exception("Testing")
        api_request = ApiRequests()
        self.assertRaises(Exception, api_request.get_access_token)

    # Tests for aws_creds.py
    @patch("sls.utils.aws_creds.ApiRequests")
    def test_get_credentials(self, mock_req):
        """
        test_get_credentials: Test setting AWS credentials
        """
        instance = mock_req.return_value
        instance.request.return_value = type(
            "Response1s", (object,), dict(text='{"credentials":{"AccessKeyId":"mock"}}')
        )
        aws_credentials = AwsCreds("test-account")
        value = aws_credentials.get_creds("test-account")
        self.assertEqual(value.get("AccessKeyId"), "mock")

    # Tests for aws_sm.py
    @patch("sls.utils.aws_sm.get_boto3_client")
    @patch("sls.utils.aws_creds.AwsCreds")
    def test_retrieve_secret(self, mock_creds, mock_boto3):
        """
        test_retrieve_secret: Test retrieve secret
        """
        client = mock_boto3.return_value
        client.get_secret_value.return_value = {
            "SecretString": "mockPwd",
            "VersionId": "oldVerId",
        }
        aws_creds = mock_creds.return_value
        aws_creds.get_creds.return_value = {"AccessKeyId": "mock"}
        sm_client = SmClient(aws_creds)
        return_secret = sm_client.retrieve_secret("Test")
        self.assertEqual(return_secret, "mockPwd")
