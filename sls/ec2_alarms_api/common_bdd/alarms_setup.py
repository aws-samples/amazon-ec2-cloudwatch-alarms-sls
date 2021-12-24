"""
    Ec2 setup and cleanup for BDD tests
"""
from sls.utils_bdd.ec2_helper import create_ec2_instance, terminate_ec2_instance

EC2_INSTANCE_DATA = {
    "AWS-7265-linux": {
        "image_id": "ami-02e136e904f3da870",
        "instance_type": "t2.nano",
        "max_count": 1,
        "min_count": 1,
        "tag_spec": [
            {
                "ResourceType": "instance",
                "Tags": [
                    {
                        "Key": "Name",
                        "Value": "linux-7265"
                    },
                    {
                        "Key": "Hostname",
                        "Value": "AWS-7265-linux"
                    }
                ]
            }
        ]
    },
    "AWS-7265-windows": {
        "image_id": "ami-0b17e49efb8d755c3",
        "instance_type": "t2.nano",
        "max_count": 1,
        "min_count": 1,
        "tag_spec": [
            {
                "ResourceType": "instance",
                "Tags": [
                    {
                        "Key": "Name",
                        "Value": "windows-7265"
                    },
                    {
                        "Key": "Hostname",
                        "Value": "AWS-7265-windows"
                    }
                ]
            }
        ]
    }

}


def create_instances(context):
    """

      Args:
          context: bdd context

      Returns:

      """
    for instance in EC2_INSTANCE_DATA:
        create_ec2_instance(context, EC2_INSTANCE_DATA[instance])


def delete_instances(context):
    """

    Args:
        context: bdd context

    Returns:

    """
    terminate_ec2_instance(context)


def delete_alarms(context):
    cloudwatch_client = context.cloudwatch_client
    alarm_names = get_alarms_names(cloudwatch_client)
    cloudwatch_client.delete_metric_alarms(alarm_names)


def get_alarms_names(cloudwatch_client):
    alarms = cloudwatch_client.client.describe_alarms(AlarmNamePrefix="itx-alarms-AWS-7265")
    alarms_names = [metric["AlarmName"] for metric in alarms["MetricAlarms"]]
    return alarms_names
