"""
This module contains behave framework function implementation
"""
# pylint:disable=no-name-in-module,import-error,wrong-import-position

import json
import os
import sys

THISDIR = os.path.dirname(__file__)  # common_bdd/
SERVDIR = os.path.dirname(THISDIR)  # ec2_alarms_api/
SLSDIR = os.path.dirname(SERVDIR)  # sls/
APPDIR = os.path.dirname(SLSDIR)  # ec2_provisioning/


sys.path.insert(0, THISDIR)
sys.path.insert(0, SERVDIR)
sys.path.insert(0, SLSDIR)
sys.path.insert(0, APPDIR)

from ec2_alarms_api.common_bdd import logger
from sls.utils_bdd.common_env import set_context, set_env_variables, set_jenkins_secret
from sls.utils.aws_cloudwatch import CloudWatchClient
from sls.utils.api_host import set_api_host
from sls.utils import get_boto3_resource
from sls.utils.aws_ec2 import EC2Client


def common_before_all(context):
    """
    This method runs before all

    Args:
        context:

    Returns:

    """
    logger.info("======================")
    logger.info("IN BEFORE ALL")
    logger.info("======================")

    env = os.environ["ENV"]
    context.env = env
    context.api_name = "ec2-alarms-api"

    with open(f"{APPDIR}/config/config.common.json") as comm_config_file:
        comm_config = json.load(comm_config_file)

    with open(f"{APPDIR}/config/config.{env}.json") as env_config_file:
        env_config = json.load(env_config_file)

    logger.info("Setting up context and environment variables")
    set_env_variables(context, comm_config, env_config)
    set_context(context, comm_config, env_config, logger)
    logger.info("Setting Jenkins Secret")
    set_jenkins_secret(context)
    logger.info("Setting cloudwatch client")
    set_cloudwatch_client(context)
    logger.info("Setting EC2 client")
    set_ec2_client_res(context)
    context.hostname_prefix = "AWS-7265-{os}"

    if context.run_behave_env != "LOCAL":
        logger.info("Setting api host")
        set_api_host(context, logger, env)


def set_cloudwatch_client(context):
    context.cloudwatch_client = CloudWatchClient(context.main_creds, context.main_region, logger)


def set_ec2_client_res(context):
    """
    Set EC2 Client and EC2 resource
    """
    aws_creds = context.main_creds
    region = context.main_region
    credentials = aws_creds.get_creds()
    context.ec2_client = EC2Client(aws_creds, region, logger)
    context.ec2_resource = get_boto3_resource("ec2", region, credentials)
