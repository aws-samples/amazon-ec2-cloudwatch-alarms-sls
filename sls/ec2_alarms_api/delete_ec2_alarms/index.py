# pylint: disable=unused-argument, protected-access, arguments-differ,no-name-in-module, import-error, wrong-import-position
"""
Handler to delete ec2 alarms api
"""

from sls.utils.lambda_handler_helper import process_api_request
from sls.utils.aws_creds import AwsCreds
from sls.utils.aws_cloudwatch import CloudWatchClient
from sls.utils.logger import Logger

logger = Logger()


def delete_alarms(event):
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

    logger.info(f"Account: {account_id}")
    logger.info(f"Region: {region}")
    logger.info(f"Hostname: {hostname}")

    cloudwatch_client = CloudWatchClient(aws_creds, region, logger)
    alarm_prefix = f"itx-alarms-{hostname}"
    alarms_names = cloudwatch_client.find_existing_alarms_list(alarm_prefix)
    cloudwatch_client.delete_metric_alarms(alarms_names)
    return f" EC2 Alarms: {alarms_names} deleted for {hostname}"


def handler(event, context):
    """
    api entry function
    """
    logger.info(context)
    output = process_api_request(event, delete_alarms, logger)
    logger.info(output)
    return output
