"""
Module to make secret manager calls
"""
# pylint: disable=unused-argument, protected-access, arguments-differ,no-name-in-module, import-error, wrong-import-position, missing-function-docstring
import logging

from sls.utils import get_boto3_client

lgr = logging.getLogger()


class SmClient:
    """
    Class to make secret manager calls
    The extra encryption/decryption of plain secret will be done within this class. Any class that
    instantiates this class will provide or expect plain password.
    """

    def __init__(self, aws_creds, secret_region=None, logger=None):
        """
        Setup for ApiRequests Class
        @param aws_creds:
        """
        self.logger = logger or lgr
        self.secret_region = "us-east-1" if secret_region is None else secret_region
        self.aws_creds = aws_creds
        self.credentials = self.aws_creds.get_creds()
        self.client = get_boto3_client(
            "secretsmanager", self.secret_region, self.credentials
        )

    def retrieve_secret(self, secret_name):
        """
        Retrieve secret from secret manager

        Args:
            secret_name:

        Returns:
            Value of the secret
        """
        secret_value = self.client.get_secret_value(SecretId=secret_name)
        return secret_value.get("SecretString")
