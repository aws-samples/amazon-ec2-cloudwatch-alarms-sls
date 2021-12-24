# pylint: disable=logging-format-interpolation, redefined-outer-name, redefined-builtin, bad-option-value, import-error
"""
Module to interact with EC2 client
"""
import boto3
import botocore.exceptions
import jmespath

from botocore.exceptions import ClientError
from sls.utils import get_boto3_client
from sls.utils.exceptions import ResourceNotFound, InvalidParameter
from sls.utils.logger import Logger

# Define default ec2 client
EC2_CLIENT = boto3.client('ec2', region_name="us-east-1")
lgr = Logger()


def is_region_valid(region, logger):
    try:
        regions = EC2_CLIENT.describe_regions(
            RegionNames=[
                region,
            ]
        )
        return regions['Regions'][0]['RegionName'] == region
    except botocore.exceptions.ParamValidationError as err:
        logger.error(err)
        return False
    except ClientError as error:
        if error.response['Error']['Code'] == 'InvalidParameterValue':
            logger.error(error)
            return False
        raise error


def get_instance_memory(instance_type, logger):
    """
    Returns memory size of the EC2 instance type in MiB

    Args:
        instance_type: Name of the instance class. Example t3.micro
        logger: Logger instance
    """
    instance_type_info = EC2_CLIENT.describe_instance_types(
        InstanceTypes=[
            instance_type,
        ]
    )
    size = instance_type_info['InstanceTypes'][0]['MemoryInfo']['SizeInMiB']
    logger.info(f"Memory in MiB for {instance_type}: {size} MiB")
    return size


class EC2Client:
    """Class to make ec2 calls"""

    def __init__(self, aws_creds, region, logger=None):
        """
        Setup for RDS Class
        @param aws_creds:
        """
        self.logger = logger or lgr
        self.region = region
        self.aws_creds = aws_creds
        self.credentials = self.aws_creds.get_creds()
        self.client = get_boto3_client("ec2", self.region, self.credentials)

    def get_running_instance_by_hostname(self, hostname):
        """
        Get the EC2 instance from the hostname in the account and region

        Args:
            hostname: EC2 Hostname tag value

        Returns:
            Json: instance details
        """
        try:
            response = self.client.describe_instances(
                Filters=[
                    {
                        "Name": "tag:Hostname",
                        "Values": [hostname]
                    },
                    {
                        "Name": "instance-state-name",
                        "Values": ["running", "rebooting"]
                    }
                ]
            )
            return response["Reservations"][0]["Instances"][0]
        except (IndexError, KeyError) as error:
            raise ResourceNotFound("Running instance with tag key: Hostname "
                                   f"and tag value: {hostname} not found") from error

        except botocore.exceptions.ParamValidationError as err:
            raise InvalidParameter(f"Hostname: {hostname} is not valid") from err
