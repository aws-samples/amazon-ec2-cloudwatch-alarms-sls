"""
Module to get apihost from cloudformation stack
"""
# pylint: disable=unused-argument, protected-access, arguments-differ,no-name-in-module,import-error, wrong-import-position

import boto3
from sls.utils.aws_creds import AwsCreds


def boto3_client(context, service, logger):
    """
    Function to get boto3 client for a specific service.

    Args:
        context:
        service:
        logger:

    Returns:
        boto3 client
    """
    aws_creds = AwsCreds(context.admin_account, logger)
    credentials = aws_creds.get_creds()
    client = boto3.client(
        service_name=service,
        region_name=context.admin_region,
        aws_access_key_id=credentials.get("AccessKeyId", ""),
        aws_secret_access_key=credentials.get("SecretAccessKey", ""),
        aws_session_token=credentials.get("SessionToken", ""),
    )
    return client


def set_api_host(context, logger, env):
    """
    sets the api host value to context

    Args:
        context:
        env:
        logger:

    Returns:

    """
    cf_client = boto3_client(context, "cloudformation", logger)
    stack_info = {}
    try:
        stack_info = cf_client.describe_stacks(StackName=context.stack_name)
        for item in stack_info["Stacks"][0]["Outputs"]:
            if item["OutputKey"] == "ServiceEndpoint":
                context.api_host = (
                    item["OutputValue"].replace("https://", "").replace(f"/{env}", "")
                )
                break
    except Exception as err:
        logger.error(
            f"An error occurred while getting cloudstack name {str(err)}, "
            f"stack_info = {str(stack_info)}"
        )
        raise err
