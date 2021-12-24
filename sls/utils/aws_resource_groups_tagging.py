"""
Module to make resource groups tagging api calls
"""
# pylint: disable=protected-access, arguments-differ,no-name-in-module, import-error, wrong-import-order, wrong-import-position

from botocore.exceptions import ClientError
from sls.utils.logger import Logger
from sls.utils import get_boto3_client
from sls.utils.exceptions import ResourceNotFound, InvalidParameter

lgr = Logger()


class ResourceGroupsTaggingClient:
    """Class to make calls to the resource groups tagging api"""

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
        self.client = get_boto3_client("resourcegroupstaggingapi",
                                       self.rds_region, self.credentials)

    def get_sns_topic_arn(self, sns_topic_tag_key, sns_topic_tag_value):
        """Get the ARN for the SNS topic that will be configured
           as the action for the Cloudwatch alarm

        Args:
            sns_topic_tag_key: The tag key on the sns topic
            sns_topic_tag_value: The tag value on the sns topic

        Returns:
            tuple:
                sns_topic_arn: The arn of the topic
                topic_found: Boolean indicating whether the SNS topic
                             with given tag key and value exists

        Raises:
            ClientError: Boto3
        """

        sns_topics = []
        sns_topic_arn = None
        paginator = self.client.get_paginator('get_resources')
        response_iterator = paginator.paginate(
            TagFilters=[
                {
                    'Key': sns_topic_tag_key,
                    'Values': [
                        sns_topic_tag_value,
                    ]
                },
            ],
            ResourceTypeFilters=[
                'sns',
            ],
        )
        for page in response_iterator:
            for topic in page.get('ResourceTagMappingList', []):
                sns_topics.append(topic.get('ResourceARN'))

        if len(sns_topics) > 0:
            sns_topic_arn = sns_topics[0]
            if len(sns_topics) > 1:
                self.logger.warning(f"Found more than one SNS topics with tag key {sns_topic_tag_key} "
                                    f"and tag value {sns_topic_tag_value}. "
                                    f"List of SNS topics: {sns_topics}."
                                    "Picked the first one for configuring backup vault "
                                    "failed jobs cloudwatch alarm : {sns_topic_arn}")
        return sns_topic_arn

    def get_resource_tags_per_arn(self, res_arn):
        """Get tags for a resource

           Args:
            res_arn: The resource arn

           Returns:
               list:
                   list of tags

           Raises:
                ClientError
           """
        try:
            resource = self.client.get_resources(
                ResourceARNList=[
                    res_arn,
                ]
            )
            tag_map_list = resource.get('ResourceTagMappingList', [])
            if len(tag_map_list) == 0:
                return []
            return tag_map_list[0].get("Tags", [])

        except ClientError as error:
            if error.response['Error']['Code'] == 'InvalidParameterException' and (
                    'AmazonResourceName' in error.response['Error']['Message']):
                raise ResourceNotFound(f"Resource not found. "
                                       f"{res_arn} is not a valid ARN.") from error
            else:
                raise

    def tag_resource_per_arn(self, res_arn, tags):
        """Tag a resource

           Args:
            res_arn: The resource arn
            tags: Dict of tags to apply

           Returns:

           Raises:
                ClientError
           """
        try:
            resource = self.client.tag_resources(
                ResourceARNList=[
                    res_arn,
                ],
                Tags=tags
            )
            failed_tags = resource.get('FailedResourcesMap', {})
            if failed_tags:
                raise InvalidParameter(f"Some tags were not applied: {failed_tags}")

        except ClientError as error:
            if error.response['Error']['Code'] == 'InvalidParameterException' and (
                    'AmazonResourceName' in error.response['Error']['Message']):
                raise ResourceNotFound(f"Resource not found. "
                                       f"{res_arn} is not a valid ARN.") from error
            else:
                raise

    def untag_resource_per_arn(self, res_arn, tag_keys):
        """UnTag a resource

           Args:
            res_arn: The resource arn
            tag_keys: list of tags keys to remove

           Returns:

           Raises:
                ClientError
           """
        try:
            resource = self.client.untag_resources(
                ResourceARNList=[
                    res_arn,
                ],
                TagKeys=tag_keys
            )
            failed_tags = resource.get('FailedResourcesMap', {})
            if failed_tags:
                raise InvalidParameter(f"Some tags couldn't be removed: {failed_tags}")

        except ClientError as error:
            if error.response['Error']['Code'] == 'InvalidParameterException' and (
                    'AmazonResourceName' in error.response['Error']['Message']):
                raise ResourceNotFound(f"Resource not found. "
                                       f"{res_arn} is not a valid ARN.") from error
            else:
                raise