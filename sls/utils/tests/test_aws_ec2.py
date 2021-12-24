# pylint: disable=missing-module-docstring, missing-function-docstring, missing-class-docstring

import logging
import unittest

from unittest.mock import patch
import os, sys
module_dir = os.path.dirname(os.path.abspath(__file__))
module_par = os.path.normpath(os.path.join(module_dir, '../../../'))
sys.path.append(module_par)
from sls.utils.aws_ec2 import is_region_valid, get_instance_memory, EC2Client
from botocore.exceptions import ClientError


class TestAwsEc2(unittest.TestCase):
    """
    Test for RdsClient
    """

    @patch("sls.utils.aws_ec2.EC2_CLIENT")
    def test_is_region_valid(self, mock_client):
        mock_client.describe_regions.return_value = {
            "Regions": [
                {
                    "RegionName": "test_region"
                }
            ]
        }
        return_result = is_region_valid("test_region", logging.getLogger())
        self.assertTrue(return_result)

    def test_invalid_parameter(self):
        self.assertFalse(is_region_valid(None, logging.getLogger()))

    @patch("sls.utils.aws_ec2.EC2_CLIENT")
    def test_client_error(self, mock_client):
        error = {
            "Error": {
                "Code": "InvalidParameterValue",
                "Message": "Invalid region",
            }
        }
        mock_client.side_effect = ClientError(error, "is_region_valid")
        return_result = is_region_valid("test_region", logging.getLogger())
        self.assertFalse(return_result)

    @patch("sls.utils.aws_ec2.EC2_CLIENT")
    def test_exception(self, mock_client):
        error = {
            "Error": {
                "Code": "OtherClientError",
                "Message": "Client error",
            }
        }
        mock_client.describe_regions.side_effect = ClientError(error, "is_region_valid")
        self.assertRaises(ClientError, is_region_valid, "test_region", logging.getLogger())

    @patch("sls.utils.aws_ec2.EC2_CLIENT")
    def test_get_instance_memory(self, mock_client):
        mock_client.describe_instance_types.return_value = {
            "InstanceTypes": [
                {
                    "MemoryInfo": {
                        "SizeInMiB": 123
                    }
                }
            ]
        }
        return_result = get_instance_memory("test_instance_type", logging.getLogger())
        self.assertEqual(return_result, 123)

    @patch("sls.utils.aws_creds.AwsCreds")
    @patch("sls.utils.aws_ec2.get_boto3_client")
    def test_get_running_instance_by_hostname(self, mock_boto3, mock_creds):
        boto3_client = mock_boto3.return_value
        aws_creds = mock_creds.return_value
        ec2_instance = {'Reservations': [
            {
                'Instances': [
                    {
                        'AmiLaunchIndex': 123,
                        'ImageId': 'string',
                        'InstanceId': 'string',
                        'Platform': 'Windows',
                        'State': {
                            'Code': 123,
                            'Name':  'running'
                        },
                    }
                ]
            }
        ]
        }

        boto3_client.describe_instances.return_value = ec2_instance
        ec2_client = EC2Client(aws_creds, "test_region")
        return_result = ec2_client.get_running_instance_by_hostname("testing")
        self.assertEqual(return_result, ec2_instance["Reservations"][0]["Instances"][0])
