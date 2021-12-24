import unittest

from unittest.mock import patch, call
import os, sys
module_dir = os.path.dirname(os.path.abspath(__file__))
module_par = os.path.normpath(os.path.join(module_dir, '../../../../'))
sys.path.append(module_par)
from sls.ec2_alarms_api.create_ec2_alarms.ec2_metrics import EC2Metrics


def get_driver_letter_name(hostname):
    return f"itx-alarms-{hostname}-{{drive_letter}}PartitionUtilizationGt85PercentFor60Mins"


def get_filesystem_name(hostname):
    return f"itx-alarms-{hostname}-{{filesystem}}DiskSpaceGt85PercentFor60Mins"


def get_status_failed_name(hostname):
    return f"itx-alarms-{hostname}-StatusCheckFailedfor10Mins"


def get_cpu_name(hostname):
    return f"itx-alarms-{hostname}-CpuUtilizationGt95PercentFor60Mins"


def get_memory_name(hostname):
    return f"itx-alarms-{hostname}-MemoryUtilizationGt95PercentFor60Mins"


class TestEC2Metrics(unittest.TestCase):
    @patch("sls.utils.aws_creds.AwsCreds")
    def setUp(self, mock_creds):
        self.aws_creds = mock_creds.return_value

    def call_create_metric(self, mock_get_instance, mock_cloudwatch, hostname,
                           platform="Windows", status="running",
                           list_metrics_return=[]):
        cloudwatch_client = mock_cloudwatch.return_value
        cloudwatch_client.list_metrics.return_value = list_metrics_return
        cloudwatch_client.find_existing_alarm_name.return_value = None

        mock_get_instance.return_value = {
            "InstanceId": "test_ec2_metrics_instance_id",
            "Platform": platform,
            "State": {
                "Code": 123,
                "Name": status
            }
        }
        ec2_metric = EC2Metrics(self.aws_creds, "test_region", hostname, "test_sns")
        config = ec2_metric.generate_alarms_conf()
        ec2_metric.create_all_alarms()
        return cloudwatch_client, config

    @patch("sls.ec2_alarms_api.create_ec2_alarms.ec2_metrics.CloudWatchClient")
    @patch("sls.ec2_alarms_api.create_ec2_alarms.ec2_metrics.EC2Metrics.get_instance")
    @patch("sls.ec2_alarms_api.create_ec2_alarms.ec2_metrics.create_metric")
    def test_hostname_without_AWS(self, mock_create_metric, mock_get_instance, mock_cloudwatch):
        hostname = "test"
        cloudwatch_client, config = self.call_create_metric(mock_get_instance, mock_cloudwatch, hostname)
        status_failed = get_status_failed_name(hostname)
        cpu_name = get_cpu_name(hostname)
        mock_create_metric.assert_has_calls(
            [
                call(cloudwatch_client, status_failed, config[status_failed]),
                call(cloudwatch_client, cpu_name, config[cpu_name])
            ],
            any_order=True
        )
        self.assertEqual(len(mock_create_metric.mock_calls), 2)

    @patch("sls.ec2_alarms_api.create_ec2_alarms.ec2_metrics.CloudWatchClient")
    @patch("sls.ec2_alarms_api.create_ec2_alarms.ec2_metrics.EC2Metrics.get_instance")
    @patch("sls.ec2_alarms_api.create_ec2_alarms.ec2_metrics.create_metric")
    def test_hostname_with_AWS(self, mock_create_metric, mock_get_instance, mock_cloudwatch):
        hostname = "AWS_test"
        cloudwatch_client, config = self.call_create_metric(mock_get_instance, mock_cloudwatch, hostname)
        status_failed = get_status_failed_name(hostname)
        cpu_name = get_cpu_name(hostname)
        memory_name = get_memory_name(hostname)
        mock_create_metric.assert_has_calls(
            [
                call(cloudwatch_client, status_failed, config[status_failed]),
                call(cloudwatch_client, cpu_name, config[cpu_name]),
                call(cloudwatch_client, memory_name, config[memory_name])
            ],
            any_order=True
        )
        self.assertEqual(len(mock_create_metric.mock_calls), 3)

    @patch("sls.ec2_alarms_api.create_ec2_alarms.ec2_metrics.EC2Metrics.get_disk_space_config")
    @patch("sls.ec2_alarms_api.create_ec2_alarms.ec2_metrics.CloudWatchClient")
    @patch("sls.ec2_alarms_api.create_ec2_alarms.ec2_metrics.EC2Metrics.get_instance")
    @patch("sls.ec2_alarms_api.create_ec2_alarms.ec2_metrics.create_metric")
    def test_drive_letter(self, mock_create_metric, mock_get_instance, mock_cloudwatch, mock_disk_space):
        hostname = "AWS_test"
        mock_disk_space.return_value = {}
        list_metrics_return = [
            {"Dimensions": [
                {"Name": "InstanceId", "Value": "test_instance_id"},
                {"Name": "DriveLetter", "Value": "E"}
            ]
            },
            {
                "Dimensions": [
                    {"Name": "InstanceId", "Value": "test_instance_id"},
                    {"Name": "DriveLetter", "Value": "F"}
                ]
            }
        ]
        self.call_create_metric(mock_get_instance, mock_cloudwatch,
                                hostname, list_metrics_return=list_metrics_return)

        self.assertEqual(len(mock_create_metric.mock_calls), 5)

    @patch("sls.ec2_alarms_api.create_ec2_alarms.ec2_metrics.EC2Metrics.get_partition_config")
    @patch("sls.ec2_alarms_api.create_ec2_alarms.ec2_metrics.CloudWatchClient")
    @patch("sls.ec2_alarms_api.create_ec2_alarms.ec2_metrics.EC2Metrics.get_instance")
    @patch("sls.ec2_alarms_api.create_ec2_alarms.ec2_metrics.create_metric")
    def test_filesystem(self, mock_create_metric, mock_get_instance, mock_cloudwatch, mock_partition):
        hostname = "AWS_test"
        mock_partition.return_value = {}
        list_metrics_return = [
            {"Dimensions": [
                {"Name": "MountPath", "Value": "/run"},
                {"Name": "InstanceId", "Value": "test_instance_id"},
                {"Name": "Filesystem", "Value": "tmpfs"}
        ]
            }

        ]
        self.call_create_metric(mock_get_instance, mock_cloudwatch,
                                hostname, platform="linux", list_metrics_return=list_metrics_return)

        self.assertEqual(len(mock_create_metric.mock_calls), 5)
