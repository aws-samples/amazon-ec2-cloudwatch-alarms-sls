"""
base init file
"""
# pylint:disable=wrong-import-position,wrong-import-order, import-error, W0703
import boto3


def get_boto3_client(service_name, secret_region, credentials=None):
    """

    :param service_name:
    :param secret_region:
    :param credentials:
    :return:
    """
    if credentials is None:
        # Use local credentials
        return boto3.Session().client(
            service_name,
            secret_region,
        )
    return boto3.client(service_name, secret_region,
                        aws_access_key_id=credentials.get('AccessKeyId', ''),
                        aws_secret_access_key=credentials.get('SecretAccessKey', ''),
                        aws_session_token=credentials.get('SessionToken', '')
                        )


def get_boto3_resource(service_name, secret_region, credentials=None):
    """

    :param service_name:
    :param secret_region:
    :param credentials:
    :return:
    """
    if credentials is None:
        # Use local credentials
        return boto3.Session().client(
            service_name,
            secret_region,
        )
    return boto3.resource(service_name, secret_region,
                          aws_access_key_id=credentials.get('AccessKeyId', ''),
                          aws_secret_access_key=credentials.get('SecretAccessKey', ''),
                          aws_session_token=credentials.get('SessionToken', '')
                          )
