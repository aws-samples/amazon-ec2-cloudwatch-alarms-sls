""" custom exceptions for rds metadata api"""

# pylint:disable=R0801
import traceback


class SecretNotFound(Exception):
    """Secret Not Found exception"""


class NonVPCxKeyExistsWithSameAlias(Exception):
    """Non VPCx Key Exists With Same Alias exception"""


class InvalidAccount(Exception):
    """Invalid account exception"""


class InvalidRegion(Exception):
    """Invalid region exception"""


class Unauthorized(Exception):
    """Unauthorized exception"""


class InvalidParameter(Exception):
    """Parameter not valid"""


class DatabaseNotAvailable(Exception):
    """Database Not Available exception"""


class DatabaseNotFound(Exception):
    """Database Not Found exception"""


class DBClusterNotFoundFault(Exception):
    """Database Cluster Not Found exception"""


class DBInstanceNotFoundFault(Exception):
    """Database Cluster Not Found exception"""


class DBInstanceNotFound(Exception):
    """Database Instance Not Found exception"""


class AccountNotFound(Exception):
    """Account Not Found exception"""


class ResourceNotFound(Exception):
    """Resource Not Found exception"""


class ClusterExists(Exception):
    """Cluster exists"""


class InstanceExists(Exception):
    """Instance exists"""


class SnsTopicNotFound(Exception):
    """Sns topic not found in account"""


def get_exception_details() -> str:
    """
    Get Exception details in formatted pattern

    Returns:
        traceback: Reformatted Exception details.
    """
    return traceback.format_exc()
