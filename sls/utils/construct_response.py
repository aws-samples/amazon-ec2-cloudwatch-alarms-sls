"""
Module to construct HTTP responses
"""
import json


class ConstructResponse:
    """Class to construct api responses"""

    def __init__(self, logger):
        self.logger = logger

    def construct_response(self, code, key, value):
        """
        Args:
           code: A valid integer HTTP status code
           key: Response data entrypoint, eg: 'error' or 'DBAs'
           value: Arbitrary data which is JSON serializable
        Returns:
          API Gateway integration response

        """
        return {
            "statusCode": code,
            "headers": self.get_response_headers(),
            "body": json.dumps({key: value})
        }

    def construct_error_response(self, error_code, error_message):
        """
            Args:
               error_code: A valid integer HTTP status code
               error_message: Error message.

            Returns:
              API Gateway integration response

            """
        return {
            "statusCode": error_code,
            "headers": self.get_response_headers(),
            "body": json.dumps({'error': error_message})
        }

    def get_response_headers(self):
        """
        Args:
        Returns:
           header for response message
        """
        return {
            "Content-Type": "application/json",
            "request-context-id": self.logger.get_uuid()
        }
