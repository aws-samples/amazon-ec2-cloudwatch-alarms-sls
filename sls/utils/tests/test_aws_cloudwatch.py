# pylint: disable=missing-module-docstring, missing-function-docstring, missing-class-docstring
import unittest

from unittest.mock import patch, Mock
import os, sys
module_dir = os.path.dirname(os.path.abspath(__file__))
module_par = os.path.normpath(os.path.join(module_dir, '../../../'))
sys.path.append(module_par)
from sls.utils.aws_cloudwatch import CloudWatchClient


def get_testing_alarm_config():
    return {
        "MetricName": "TestingMetric",
        "Statistic": "Average",
        "Namespace": "testing_namespace",
        "Period": 300,
        "EvaluationPeriods": 12,
        "Threshold": 95,
        "ThresholdDesc": "95Percent",
        "ComparisonOperator": "GreaterThanThreshold",
        "Unit": "Percent"
    }


def get_testing_default_actions():
    config = get_testing_alarm_config()
    config.update({
        "AlarmActions": ["testing_action"],
        "AlarmDescription": "testing_dimension_value TestingMetric Gt 95Percent for 60 mins",
        "InsufficientDataActions": ["testing_action"],
        "OKActions": ["testing_action"],
        "Dimensions":
            [
                {
                    "Name": "testing_dimension_name",
                    "Value": "testing_dimension_value"
                }
            ]
    })
    del config["ThresholdDesc"]
    return config


MockAwsCreds = Mock()
MockBoto3 = Mock()


@patch("sls.utils.aws_creds.AwsCreds", new=MockAwsCreds)
@patch("sls.utils.aws_cloudwatch.get_boto3_client", new=MockBoto3)
class TestCloudWatchClient(unittest.TestCase):
    def setUp(self):
        self.aws_creds = MockAwsCreds.return_value
        self.region = "test_region"

    def test_create_metric_alarm(self):
        alarm_conf = {
            "MetricName": "TestingMetric"
        }
        alarm_name = "testing"
        boto3_client = MockBoto3.return_value
        waiter = boto3_client.get_waiter.return_value
        waiter.wait.return_value = True
        boto3_client.describe_alarms.return_value = {}
        cloudwatch_client = CloudWatchClient(self.aws_creds, self.region)
        cloudwatch_client.create_metric_alarm(alarm_name, **alarm_conf)
        boto3_client.put_metric_alarm.assert_called_with(AlarmName=alarm_name, **alarm_conf)

    def test_delete_metric_alarms(self):
        alarm_name = "testing"
        boto3_client = MockBoto3.return_value
        boto3_client.describe_alarms.return_value = {}
        cloudwatch_client = CloudWatchClient(self.aws_creds, self.region)
        cloudwatch_client.delete_metric_alarms(alarm_name)
        boto3_client.delete_alarms.assert_called_with(AlarmNames=[alarm_name])

    def test_find_existing_alarm_name(self):
        alarm_prefix = "testing"
        boto3_client = MockBoto3.return_value
        boto3_client.describe_alarms.return_value = {
            "MetricAlarms": [
                {
                    "EvaluationPeriods": 2,
                    "AlarmName": "testingAlarmName"

                }
            ]
        }
        cloudwatch_client = CloudWatchClient(self.aws_creds, self.region)
        alarm_name = cloudwatch_client.find_existing_alarm_name(alarm_prefix)
        self.assertEqual(alarm_name, "testingAlarmName")
