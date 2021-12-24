# pylint: disable=unused-argument, protected-access, arguments-differ,no-name-in-module, import-error, wrong-import-position
"""
Helper functions for Lambda helper
"""
import traceback

from sls.utils.auth import authorize_lambda
from sls.utils.construct_response import ConstructResponse
from sls.utils.aws_ec2 import is_region_valid
from sls.utils.exceptions import (InvalidAccount, Unauthorized,
                              InvalidRegion, DatabaseNotFound,
                              InvalidParameter, ResourceNotFound)


def set_logger_context_id(event, logger):
    """
    Set the logger to request-context-id if in headers

    Args:
        event: API gateway proxy event
        logger:

    Returns:
    """
    headers = event.get('headers', {})
    request_context_id = headers.get('request-context-id')
    if request_context_id:
        logger.set_uuid(request_context_id)
    return logger


def process_api_request(event, func, logger):
    """
    Create alarms for 2 RDS metrics: CPUUtilization, FreeStorageSpace

    Args:
        event: API gateway proxy event
        func: function to call to process api request
        logger

    Returns:
    """
    # set logger id
    logger = set_logger_context_id(event, logger)

    # initiate Construct response
    const_resp = ConstructResponse(logger)

    # Validate
    try:
        path_params = event.get('pathParameters', {})
        account_id = path_params.get('account_id')
        region = path_params.get("region_name")
        if not account_id:
            raise InvalidAccount(f"Account not found: {account_id}")
        authorize_lambda(event)
        if not is_region_valid(region, logger):
            raise InvalidRegion(f"Region not found: {region}")
        output = func(event)

    except Unauthorized as exc:
        traceback.print_exc()
        return const_resp.construct_error_response(401, str(exc))

    except InvalidParameter as exc:
        traceback.print_exc()
        return const_resp.construct_error_response(400, str(exc))

    except (DatabaseNotFound,  InvalidRegion,
            InvalidAccount, ResourceNotFound) as exc:
        traceback.print_exc()
        return const_resp.construct_error_response(404, str(exc))

    except Exception as exc:
        traceback.print_exc()
        return const_resp.construct_error_response(500, str(exc))

    return const_resp.construct_response(200, "message", output)

