# pylint: disable=missing-module-docstring, missing-function-docstring, missing-class-docstring

import logging

from unittest.mock import patch
from unittest.mock import MagicMock
import os, sys
module_dir = os.path.dirname(os.path.abspath(__file__))
module_par = os.path.normpath(os.path.join(module_dir, '../../../'))
sys.path.append(module_par)
from sls.utils.api_host import set_api_host


def get_stack_info():
    return {
        'Stacks': [
            {
                'StackId': 'string',
                'StackName': 'string',
                'ChangeSetId': 'string',
                'Description': 'string',
                'Outputs': [
                    {
                        'OutputKey': 'ServiceEndpoint',
                        'OutputValue': 'https://testing/dev',
                        'Description': 'string',
                        'ExportName': 'string'
                    },
                ]
            }
        ]
    }


@patch("sls.utils.api_host.boto3_client")
def test_set_api_host(mock_boto3):
    client = mock_boto3.return_value
    client.describe_stacks.return_value = get_stack_info()
    mock_context = MagicMock()
    mock_context.stack_name = "testing_stack"
    expected_host = "testing"
    logger = logging.getLogger()
    set_api_host(mock_context, logger, "dev")
    assert expected_host == mock_context.api_host
