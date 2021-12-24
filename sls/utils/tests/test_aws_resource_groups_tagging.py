import unittest

from unittest.mock import patch
from sls.utils.aws_resource_groups_tagging import ResourceGroupsTaggingClient
from sls.utils.exceptions import InvalidParameter, ResourceNotFound
from botocore.exceptions import ClientError

class TestResourceGrpTagClient(unittest.TestCase):
    @patch("sls.utils.aws_resource_groups_tagging.get_boto3_client")
    @patch("sls.utils.aws_creds.AwsCreds")
    def test_get_sns_topic_arn(self, mock_creds, mock_boto3):
        aws_creds = mock_creds.return_value
        aws_creds.get_creds.return_value = {"AccessKeyId": "mock"}

        client = mock_boto3.return_value
        paginator = client.get_paginator.return_value
        paginator.paginate.return_value = [
            {
                'ResourceTagMappingList': [
                    {
                        'ResourceARN': 'testing_sns_topic_arn',
                    },
                ]
            }
        ]

        region = "testing"
        rgt_client = ResourceGroupsTaggingClient(aws_creds, region)
        topic_arn = rgt_client.get_sns_topic_arn("testing_key", "testing_value")
        self.assertEqual(topic_arn, 'testing_sns_topic_arn')

    @patch("sls.utils.aws_resource_groups_tagging.get_boto3_client")
    @patch("sls.utils.aws_creds.AwsCreds")
    def test_get_resource_tags_per_arn(self, mock_creds, mock_boto3):
        aws_creds = mock_creds.return_value
        aws_creds.get_creds.return_value = {"AccessKeyId": "mock"}

        client = mock_boto3.return_value
        client_return_value = {
            'ResourceTagMappingList': [
                {
                    'ResourceARN': 'test_arn',
                    'Tags': [
                        {
                            'Key': 'test_key',
                            'Value': 'test_value'
                        },
                    ]
                }
            ]
        }
        client.get_resources.return_value = client_return_value
        region = "testing"
        rgt_client = ResourceGroupsTaggingClient(aws_creds, region)
        returned_tags = rgt_client.get_resource_tags_per_arn("test_arn")
        expected_tags = client_return_value['ResourceTagMappingList'][0]['Tags']
        self.assertEqual(returned_tags, expected_tags)

    @patch("sls.utils.aws_resource_groups_tagging.get_boto3_client")
    @patch("sls.utils.aws_creds.AwsCreds")
    def test_tag_failure(self, mock_creds, mock_boto3):
        aws_creds = mock_creds.return_value
        aws_creds.get_creds.return_value = {"AccessKeyId": "mock"}

        client = mock_boto3.return_value
        client_return_value = {
            'FailedResourcesMap':
                {
                    'string': {
                        'StatusCode': 123,
                        'ErrorCode': 'InvalidParameterException',
                        'ErrorMessage': 'string'
                    }

                }
        }
        client.tag_resources.return_value = client_return_value
        region = "testing"
        rgt_client = ResourceGroupsTaggingClient(aws_creds, region)
        self.assertRaises(InvalidParameter, rgt_client.tag_resource_per_arn, "test_arn", "test_tags")
        self.assertRaises(InvalidParameter, rgt_client.untag_resource_per_arn, "test_arn", "test_keys")

    @patch("sls.utils.aws_resource_groups_tagging.get_boto3_client")
    @patch("sls.utils.aws_creds.AwsCreds")
    def test_invalid_arn(self, mock_creds, mock_boto3):
        aws_creds = mock_creds.return_value
        aws_creds.get_creds.return_value = {"AccessKeyId": "mock"}

        error = {
            "Error": {
                "Code": "InvalidParameterException",
                "Message": "Not a valid AmazonResourceName",
            }
        }
        client = mock_boto3.return_value
        client.get_resources.side_effect = ClientError(error, "invalid_arn")
        client.tag_resources.side_effect = ClientError(error, "invalid_arn")
        client.untag_resources.side_effect = ClientError(error, "invalid_arn")

        region = "testing"
        rgt_client = ResourceGroupsTaggingClient(aws_creds, region)
        self.assertRaises(ResourceNotFound, rgt_client.get_resource_tags_per_arn, "test_arn")
        self.assertRaises(ResourceNotFound, rgt_client.tag_resource_per_arn, "test_arn", "test_tags")
        self.assertRaises(ResourceNotFound, rgt_client.untag_resource_per_arn, "test_arn", "test_keys")

