# pylint: disable=unused-argument, protected-access, arguments-differ,no-name-in-module, import-error, wrong-import-position
"""
Handler for ec2 alarms api
"""

from sls.utils.lambda_handler_helper import process_api_request
from sls.utils.aws_creds import AwsCreds
from sls.utils.aws_resource_groups_tagging import ResourceGroupsTaggingClient
from sls.ec2_alarms_api.create_ec2_alarms.ec2_metrics import EC2Metrics
from sls.utils.exceptions import SnsTopicNotFound
from sls.utils.logger import Logger

logger = Logger()
SNS_TOPIC_TAG_KEY = "vpcx-Cloudwatch-Alarm-Topic"
SNS_TOPIC_TAG_VALUE = "true"


def get_sns_topic_arn(aws_creds, ec2_region):
    """
    Retrieves the sns topic arn for the account
    """
    rgt_client = ResourceGroupsTaggingClient(aws_creds, ec2_region, logger)
    sns_topic_arn = rgt_client.get_sns_topic_arn(SNS_TOPIC_TAG_KEY, SNS_TOPIC_TAG_VALUE)
    if not sns_topic_arn:
        raise SnsTopicNotFound(f"Account doesn't have the SNS topic tagged with "
                               f"key: '{SNS_TOPIC_TAG_KEY}' and value: '{SNS_TOPIC_TAG_VALUE}'")
    return sns_topic_arn


def create_alarms(event):
    """
    Create the alarms

    Args:
        event: API gateway proxy event

    Returns:
    """
    path_params = event.get('pathParameters', {})
    account_id = path_params.get('account_id')
    region = path_params.get('region_name')
    hostname = path_params.get('ec2_hostname')

    aws_creds = AwsCreds(account_id, logger)
    sns_topic_arn = get_sns_topic_arn(aws_creds, region)

    logger.info(f"Account: {account_id}")
    logger.info(f"Region: {region}")
    logger.info(f"Hostname: {hostname}")

    ec2_metrics = EC2Metrics(aws_creds, region, hostname, sns_topic_arn, logger)
    return ec2_metrics.create_all_alarms()


def handler(event, context):
    """
    api entry function
    """
    logger.info(context)
    output = process_api_request(event, create_alarms, logger)
    logger.info(output)
    return output
