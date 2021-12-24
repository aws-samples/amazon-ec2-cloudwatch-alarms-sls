"""
    EC2 utilities functions for bdd
"""


# pylint: disable=wrong-import-position,no-value-for-parameter

def create_ec2_instance(context, db_info):
    ec2_resource = context.ec2_resource
    res = ec2_resource.create_instances(
        ImageId=db_info.get('image_id'),
        InstanceType=db_info.get('instance_type'),
        MaxCount=db_info.get('max_count'),
        MinCount=db_info.get('min_count'),
        SecurityGroupIds=context.sg_name,
        SubnetId=context.subnet_id,
        TagSpecifications=db_info.get("tag_spec", [])
    )
    context.ec2_instance_ids.append(res[0].id)
    waiter = context.ec2_client.client.get_waiter('instance_running')
    waiter.wait(InstanceIds=[res[0].id])


def terminate_ec2_instance(context):
    ec2_client = context.ec2_client
    ec2_client.client.terminate_instances(InstanceIds=context.ec2_instance_ids)
    ec2_waiter = ec2_client.client.get_waiter('instance_terminated')
    ec2_waiter.wait(InstanceIds=context.ec2_instance_ids, WaiterConfig={'Delay': 60})
