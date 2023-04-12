"""
Module to create metrics alarms for ec2
"""
# pylint: disable=protected-access, arguments-differ,no-name-in-module, import-error, wrong-import-position
import json
import os
import re
import uuid
import concurrent.futures
import jmespath
from jinja2 import Environment, FileSystemLoader

from sls.utils.aws_cloudwatch import CloudWatchClient
from sls.utils.aws_ec2 import EC2Client
from sls.utils.logger import Logger
from sls.utils.exceptions import InvalidParameter

lgr = Logger()
THISDIR = os.path.dirname(__file__)  # create_ec2_alarms/


class EC2Metrics:
    """
    Create metric alarms for EC2 instances
    """

    def __init__(self, aws_creds, ec2_region, hostname, sns_topic_arn, logger=None):
        """
        Set up clients to create the ec2 metric alarms

        Args:
            aws_creds: instance of AwsCreds
            ec2_region: Aws Region for the client
            hostname: value of the tag key Hostname for the instance
            sns_topic_arn: Cloudwatch alarm sns topic arn
            logger: instance of Logger
        """
        self.logger = logger or lgr
        self.cloudwatch_client = CloudWatchClient(aws_creds, ec2_region, self.logger)
        self.hostname = hostname
        self.aws_creds = aws_creds
        self.ec2_region = ec2_region
        self.instance = self.get_instance()
        self.sns_topic_arn = sns_topic_arn

    def get_instance(self):
        """
        Retrieves the instance details using the hostname
        """
        ec2_client = EC2Client(self.aws_creds, self.ec2_region, self.logger)
        return ec2_client.get_running_instance_by_hostname(self.hostname)

    def create_all_alarms(self):
        """
        Retrieve a dict of the alarms configuration using generate_alarms_conf
        Create the alarms for each key-value pair: the key is the alarm name
        and the value is the configuration for the alarm
        """
        self.logger.info("Generating the alarms configuration for the instance")
        alarms_conf = self.generate_alarms_conf()

        self.logger.info(f"Creating {len(alarms_conf)} alarms for the instance with config: {alarms_conf}")
        failed_alarms = []
        with concurrent.futures.ThreadPoolExecutor() as executor:
            future_to_alarm = {executor.submit(create_metric, self.cloudwatch_client,
                                               alarm_name, config): alarm_name
                               for alarm_name, config in alarms_conf.items()}
            for future in concurrent.futures.as_completed(future_to_alarm):
                alarm_name = future_to_alarm[future]
                try:
                    future.result()
                except Exception as exc:
                    failed_alarms.append({alarm_name: exc})

        if failed_alarms:
            raise Exception(f"Some alarms not created for {self.hostname}. "
                            f"FailedAlarms: {failed_alarms}. InstanceId: {self.get_instance_id()}")
        return f"Alarms created for {self.hostname}"

    def generate_alarms_conf(self):
        """
        Import the jinja template for configuration and replace variable
        """
        fileloader = FileSystemLoader(searchpath=f"{THISDIR}/jinja_templates")
        template_env = Environment(loader=fileloader, trim_blocks=True,
                                   lstrip_blocks=True, autoescape=True)
        alarm_config_template = template_env.get_template("alarm_config_template.jinja2")
        alarm_config = alarm_config_template.render(instance=self)
        self.logger.info(alarm_config)
        return json.loads(alarm_config)

    def get_partition_config(self):
        """
        Retrieve the list of metrics defined for PartitionUtilization
        that have DriveLetter dimension
        Returns:
            list : dict of the alarmName, dimension value and dimensions
        """
        metric_filter = {"Namespace": "System/Windows",
                         "MetricName": "PartitionUtilization",
                         "Dimensions": [
                             {"Name": "InstanceId", "Value": f"{self.get_instance_id}"},
                             {"Name": "DriveLetter"}
                         ]
                         }

        return self.get_metric_config(metric_filter, "DriveLetter", "PartitionUtilizationGt85PercentFor60Mins")

    def get_disk_space_config(self):
        """
        Generate the alarm configuration for the DiskSpaceUtilization metric
        Returns:
            dict: key-value pair of alarm configuration and alarm name
        """
        metric_filter = {"Namespace": "System/Linux",
                         "MetricName": "DiskSpaceUtilization",
                         "Dimensions": [
                             {"Name": "InstanceId", "Value": f"{self.get_instance_id}"},
                             {"Name": "Filesystem"}
                         ]
                         }
        return self.get_metric_config(metric_filter, "Filesystem", "DiskSpaceGt85PercentFor60Mins")

    def get_metric_config(self, metric_filter, dimension_name, metric_desc_suffix):
        """
           Return list of dict with alarm name, dimension value and dimensions
           Args:
               metric_filter: filter to retrieve the metrics
               dimension_name: the dimension name to retrieve. Ex: DriveLetter
               metric_desc_suffix: description for the metric. Ex PartitionUtilizationGt85PercentFor60Mins
           Returns:
               List : dict for each metric
       """
        metric_conf = []
        metrics = self.cloudwatch_client.list_metrics(metric_filter)
        for metric in metrics:
            dimension_value = get_dimension_value(metric, dimension_name)
            prefix = f"{self.generate_alarm_prefix()}-{dimension_value}-{metric_desc_suffix}"
            alarm_name = self.get_alarm_name(prefix)
            metric_conf.append({"alarmName": alarm_name,
                                "dimensionValue": dimension_value,
                                "dimensions": json.dumps(metric["Dimensions"])})
        return metric_conf

    def get_instance_id(self):
        """
        Returns the instance id
        """
        return self.instance["InstanceId"]

    def get_memory_namespace(self):
        """
        Returns the namespace based on the instance platform
        """
        if self.is_windows_platform():
            return "System/Windows"

        return "System/Linux"

    def is_windows_platform(self):
        """
        Check if key is present
        """
        return "Platform" in self.instance and self.instance["Platform"] == "Windows"

    def get_default_actions(self):
        return f""" "AlarmActions": ["{self.sns_topic_arn}"],
        "OKActions": ["{self.sns_topic_arn}"]"""

    def get_base_dimension(self):
        return f""""Dimensions":[
                    {{"Name": "InstanceId",
                        "Value": "{self.get_instance_id()}"
                    }}
                    ]"""

    def generate_alarm_prefix(self):
        """
        Generate the cloudwatch alarm name prefix

        """
        return f"itx-alarms-{self.hostname}"

    def get_alarm_name(self, prefix):
        """
        Return alarm name for metric with same potential metric
        """
        existing_name = self.cloudwatch_client.find_existing_alarm_name(prefix)
        if not existing_name:
            return prefix + "-" + str(uuid.uuid1())
        return existing_name


def get_dimension_value(metric, dimension):
    """
    Retrieves the dimension for DriveLetter and Filesystem metric

    Args:
           metric: a Cloudwatch metric dict
           dimension: the dimension to retrieve

    When creating an alarm, the name cannot exceed 255 characters. Because
    we don't know how long the filesystem name will be, to be safe we will only
    use the first 5 characters of the last section of the filesystem.
    If not a filesystem (no / in input_string) we return the input_string
    """
    dimension_value = jmespath.search(f"Dimensions[?Name == '{dimension}'].Value", metric)
    input_string = dimension_value[0]
    try:
        if input_string == '/':
            return ''
        s_l = input_string.split('/')
        if len(s_l) <= 1:
            return alphanum_string(s_l[0])
        return alphanum_string(s_l[len(s_l) - 1][0:5])
    except Exception:
        return ''


def alphanum_string(input_string):
    """
    Removes all non-alphanumeric characters from the given string.
    """
    pattern = re.compile(r'[\W_]+')
    return pattern.sub('', input_string)


def create_metric(client, name, config):
    client.create_metric_alarm(name, **config)
