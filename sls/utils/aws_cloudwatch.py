"""
Module to make cloudwatch calls
"""
# pylint: disable=protected-access, arguments-differ,no-name-in-module, import-error, wrong-import-position
import time
import jmespath

from sls.utils.logger import Logger
from sls.utils import get_boto3_client

lgr = Logger()


class CloudWatchClient:
    """Class to make calls to Cloudwatch"""

    def __init__(self, aws_creds, rds_region, logger=None):
        """
        Set up client

        Args:
            aws_creds: AwsCreds instance
            rds_region: Aws Region for the client
            logger: Logger instance
        """
        self.logger = logger or lgr
        self.rds_region = rds_region
        self.aws_creds = aws_creds
        self.credentials = self.aws_creds.get_creds()
        self.client = get_boto3_client("cloudwatch", self.rds_region, self.credentials)

    def create_metric_alarm(self, alarm_name, **kwargs):
        """Create Cloudwatch alarm

             Args:
                 alarm_name: name of the alarm
                 kwargs: other properties of the alarm

             Returns:

             Raises:
                 ClientError: Boto3 error
        """

        self.client.put_metric_alarm(AlarmName=alarm_name, **kwargs)
        waiter = self.client.get_waiter('alarm_exists')
        waiter.wait(
            AlarmNames=[
                alarm_name,
            ])

    def alarms_exist(self, **kwargs):
        """
        Checks if alarm exists
        Args:
                 kwargs: describe_alarms parameters
        """
        response = self.client.describe_alarms(**kwargs)
        return len(response.get('CompositeAlarms', [])) > 0 or len(response.get('MetricAlarms', [])) > 0

    def find_existing_alarm_name(self, prefix):
        """
        Check to see if a MetricAlarm with  prefix already exists

        Returns:
            String: the alarm name if one alarm is found with the prefix else None
        """
        alarms = self.find_existing_alarms_list(prefix)
        if len(alarms) == 1:
            return alarms[0]

    def find_existing_alarms_list(self, prefix):
        """
        Return the list of alarm names matching a prefix

        Returns:
            List: alarms names
        """
        alarms = self.client.describe_alarms(AlarmNamePrefix=prefix)
        return jmespath.search("MetricAlarms[].AlarmName", alarms)

    def delete_metric_alarms(self, alarm_name):
        """
        Deletes a list of alarms
        Args:
                 alarm_name: single alarm of a list of alarm
        """
        if isinstance(alarm_name, str):
            names = [alarm_name]
        else:
            names = alarm_name
        try:
            self.client.delete_alarms(
                AlarmNames=names
            )
        except self.client.exceptions.ResourceNotFound:
            self.logger.info(f"At least one alarm not found for {names}")
        self.logger.info(f"waiting for alarms to be deleted")
        number_of_retries = 25
        alarm_found = True
        while alarm_found and number_of_retries <= 25:
            time.sleep(5)
            alarm_found = self.alarms_exist(AlarmNames=names)
            number_of_retries += 1
            self.logger.info(f"Deleting alarm: {names}")

    def list_metrics(self, kwargs):
        """List Cloudwatch alarm

             Args:
                 kwargs: properties of metrics in this format
                 {Namespace:'string',
                  MetricName:'string',
                  Dimensions:[
                    {
                        'Name': 'string',
                        'Value': 'string'
                    } ]
                 }

             Returns:
                 list: of alarms matching the search

             Raises:
                 ClientError: Boto3 error
        """
        response = self.client.list_metrics(**kwargs)
        return response["Metrics"]
