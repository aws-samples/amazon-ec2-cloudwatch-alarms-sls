"""
Module to get credentials required to make rds, s3, sm calls
"""
# pylint: disable=unused-argument, protected-access, arguments-differ,no-name-in-module, import-error
import json
import os

from sls.utils.api_request import ApiRequests
from sls.utils.exceptions import InvalidAccount
from sls.utils.logger import Logger

lgr = Logger()

class AwsCreds:
    """Class to get credentials required to make rds, sm calls"""

    def __init__(self, account, logger=None):
        """
        Setup for ApiRequests Class
        """
        self.logger = logger or lgr
        self.vpcxiam_endpoint = os.environ.get("vpcxiam_endpoint")
        self.vpcxiam_scope = os.environ.get("vpcxiam_scope")
        self.vpcxiam_host = os.environ.get("vpcxiam_host")
        self.account = account
        self.api_requests = ApiRequests(self.logger)

    def get_creds(self, account=None):
        """
        Get credentials for lambda function to use when using AWS service in target account

        Args:
            account:

        Returns:

        """
        target_account = account or self.account
        url = (
            self.vpcxiam_endpoint
            + f"/v1/accounts/{target_account}/roles/admin/credentials"
        )
        scope = self.vpcxiam_scope
        additional_headers = {"Host": self.vpcxiam_host}
        try:

            creds = json.loads(
                (
                    self.api_requests.request(
                        url=url,
                        method="get",
                        scope=scope,
                        additional_headers=additional_headers,
                        additional_payload={'duration': 3600}
                    )
                ).text
            )
            error = creds.get("error", {})
            if error:
                raise Exception(error)
            credentials = creds.get("credentials", {})
            if credentials:
                return credentials
        except Exception as error:
            self.logger.info(
                f"Error retrieving credentials for account {target_account}"
            )
            self.logger.warn(error)
            if "Invalid account" in error.args[0]:
                raise InvalidAccount(f"Account not found: {target_account}") from error
            raise error
        raise Exception("Credentials not retrieved")
