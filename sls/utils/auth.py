# pylint: disable=logging-format-interpolation, redefined-outer-name, redefined-builtin, bad-option-value, import-error
"""
Module for retrieving LDAP credential
"""
import logging
import json
import os
import boto3

#from cloudx_sls_authorization import lambda_auth
from sls.utils.exceptions import Unauthorized

# Initialize Logger
LOGGER = logging.getLogger()
LOGGER.setLevel(logging.INFO)

# Define secrets client
SECRETS_CLIENT = boto3.client('secretsmanager')


def retrieve_azure_auth_credentials():
    """
    Retrieve password from secrets manager

    Args:

    Returns:
         string: password
    """
    azure_auth_secret_name = os.environ.get('AZURE_AUTH_SECRET_NAME')
    secret_response = SECRETS_CLIENT.get_secret_value(
        SecretId=azure_auth_secret_name
    )
    secret = json.loads(secret_response['SecretString'])
    return secret['client_secret']


def format_ldap_group_names(event):
    """
       Replace account_id value in LDAP_GROUP_NAME

       Args:
            event: Event from Lambda proxy input

       Returns:
           List: formatted ldap groups
       """
    path_params = event.get('pathParameters', {})
    account_id = path_params.get('account_id')
    ldap_group_name = os.environ.get('LDAP_GROUP_NAME')
    if account_id:
        formatted_group_names = ldap_group_name.format(project_id=account_id)
    return formatted_group_names.split(',')


def authorize_lambda(event):
    """
    Verifies token signature and returns token information.

    Args:
        event: Lambda event from API Gateway

    Returns:
        bool: is request allowed
    """
    group_names = format_ldap_group_names(event)
    azure_auth_secret = retrieve_azure_auth_credentials()
    azure_auth_client_id = os.environ.get('AZURE_AUTH_CLIENT_ID')

    msft_idp_tenant_id = os.environ.get('MSFT_IDP_TENANT_ID')
    msft_idp_app_id = os.environ.get('MSFT_IDP_APP_ID', "").split(',')
    msft_idp_client_roles = os.environ.get('MSFT_IDP_CLIENT_ROLES', "").split(',')

    try:
        # return lambda_auth.authorize_lambda_request_v2(event, msft_idp_tenant_id, msft_idp_app_id,
        #                                                msft_idp_client_roles, azure_auth_client_id,
        #                                                azure_auth_secret, group_names)
        pass
    except Exception as exc:
        raise Unauthorized(f"UNAUTHORIZED (User/App Token Unauthorized):{exc}") from exc
