"""
This module is used to do API calls to AWSAPI Microservices
"""
# pylint:disable= no-member, invalid-name, E0401, W1203, C0411
import logging
import os
import time
import boto3

#from cloudx_sls_authorization.create_token import get_bearer_token
from flask import Response
from requests import request as req

HTTP_GET = "get"
HTTP_PUT = "put"
HTTP_POST = "post"

lgr = logging.getLogger()
lgr.setLevel(logging.INFO)


def boto_session_client(region, secret_name):
    """
    Create boto client using a session

    Args:
        region:
        secret_name:

    Returns:

    """
    session = boto3.Session()
    return (
        session.client("secretsmanager", region)
            .get_secret_value(SecretId=secret_name)
            .get("SecretString")
    )


def get_secret_value():
    """
        Retrieve the client secret value for the app

        Args:

        Returns: secret value

        """
    region_secret = os.environ.get("region_secret", "us-east-1")
    secret_name = os.environ.get(
        "app_secret_name", "clx-awsapi-ec2-provisioning"
    )
    try:
        client_secret = boto_session_client(region_secret, secret_name)
    except Exception as error:
        if "ExpiredTokenException" in error.args[0]:
            time.sleep(10)
            client_secret = boto_session_client(region_secret, secret_name)
        else:
            raise error
    return client_secret


class ApiRequests:
    """Class for Making AWSAPI Microservice Calls"""

    def __init__(self, logger=None):
        """
        Setup for ApiRequests Class
        """
        self.logger = logger or lgr
        self.token_url = os.environ.get("token_url")
        self.client_id = os.environ.get("app_client_id")
        self.scope = os.environ.get("vpcxiam_scope")
        self.client_secret = get_secret_value()

    def get_access_token(
            self, client_id: str = None, client_secret: str = None, scope: str = None
    ) -> str:
        """
        Get an Access Token for the <scope> of the client

        Args:
            client_id (str): client id to get token.
            client_secret (str): client secret to get token.
            scope (str): Azure AD App registration scope | DEFAULT = VPCxIAM Default Scope.

        Returns:
            str: Azure AD Bearer Token
        """
        if not scope:
            scope = self.scope
        if not client_id:
            client_id = self.client_id
        if not client_secret:
            client_secret = self.client_secret
        try:
            self.logger.debug(f"Generating Bearer token for scope '{scope}'.")
            # token = get_bearer_token(
            #     client_id, client_secret, token_url=self.token_url, scope=scope
            # )
            token = ""
        except Exception as ex:
            self.logger.error(
                f"get_access_token - Failed to generate token for scope {scope} at url "
                f"{self.token_url}."
                f" Error Details - {str(ex)}."
            )
            self.logger.info(
                f"error for client id {client_id} and secret {client_secret}"
            )
            raise ex
        return token

    def request(
            self,
            url: str,
            method: str,
            scope: str = None,
            additional_headers: dict = None,
            additional_payload: dict = None,
    ) -> Response:
        """
        Make a Http request to the provided url

        Args:
            url (str): API URL.
            method (str): Http method. Values = 'get'
            scope (str): AWSAPI Microservice scope for registered Azure App.
            additional_headers (dict): Additional request headers.
            additional_payload (dict): Additional request paylaod.

        Returns:
            Response: Response object of Http Request
        """
        try:
            access_token = self.get_access_token(scope=scope)
            if not access_token.startswith("Bearer "):
                access_token = "Bearer " + access_token
            headers = {
                "Content-Type": "application/json",
                "Authorization": access_token,
            }
            if additional_headers:
                headers.update(additional_headers)
            kwargs = {"verify": False, "headers": headers}
            payload = {}
            if additional_payload:
                payload.update(additional_payload)
            if method in [HTTP_PUT, HTTP_POST]:
                kwargs["json"] = payload
            elif method in [HTTP_GET]:
                kwargs["params"] = payload
            else:
                raise Exception(f"Http Method type {method} not Supported")
            self.logger.debug(
                f"Making {method.upper()} call - "
                "{"
                f"'url': '{url}', 'payload': {payload}"
                "}"
            )
            resp = req(method, url, timeout=300, **kwargs)
            if resp.status_code == 200:
                return resp
            msg = (
                f"Failed to Get credentials for Url '{url}' with "
                f"status code '{str(resp.status_code)}'. Details - '{str(resp.content)}'"
            )
            raise Exception(msg)
        except Exception as ex:
            self.logger.error(ex)
            raise ex
