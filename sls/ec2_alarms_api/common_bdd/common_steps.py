"""
Contains behave step implementation
"""
# pylint: disable = import-error,no-name-in-module,C0413,missing-function-docstring,wrong-import-order

import requests
import json
import os

from behave import then, given
from ec2_alarms_api.common_bdd import logger
from hamcrest import assert_that, equal_to, contains_string

THISDIR = os.path.dirname(__file__)  # common_bdd/
SERVDIR = os.path.dirname(THISDIR)  # ec2_alarms_api/


@given(u'{method} EC2 Alarms API exists')
def api_exists(context, method):
    logger.info(f"Formatting url for {method} Schedule API")
    api_endpoint = "v1/accounts/{account_id}/regions/{region}/instances/{ec2_hostname}/EC2Alarms"
    context.url = f"{context.vpce_endpoint}/{api_endpoint}"
    logger.info(context.url)


@given(u'valid oauth2 token for API authorization generated')
def generate_valid_auth(context):
    logger.info("Generating valid oauth2 token for API")
    context.token = context.api_req.get_access_token(client_id=context.jenkins_client_id,
                                                     client_secret=context.jenkins_client_secret,
                                                     scope=context.application_scope)


@given(u'invalid oauth2 token for API authorization generated')
def generate_invalid_auth(context):
    logger.info("Generating invalid oauth2 token for API")
    context.token = 'invalid_token'


@given(u'VPCx account is valid')
def with_valid_account(context):
    logger.info("Updating url with valid account")
    context.url = context.url.format(account_id=context.main_account, region="{region}",
                                     ec2_hostname="{ec2_hostname}")
    logger.info(context.url)


@given(u'VPCx account is not valid')
def with_invalid_account(context):
    logger.info("Updating url with invalid region")
    context.url = context.url.format(account_id="account", region="us-east-1", ec2_hostname="ec2_hostname")
    logger.info(context.url)


@given(u'Region is valid')
def with_region_valid(context):
    logger.info("Updating url with valid region")
    context.url = context.url.format(region=context.main_region, ec2_hostname="{ec2_hostname}")
    logger.info(context.url)


@given(u'Region is not valid')
def with_region_invalid(context):
    logger.info("Updating url with invalid region")
    context.url = context.url.format(region="region", ec2_hostname="ec2_hostname")
    logger.info(context.url)


@given(u'instance not valid')
def db_exists(context):
    context.url = context.url.format(ec2_hostname="invalid-hostname")
    logger.info(context.url)


@given(u'VPCx managed alarm {raw_name} does not exist')
def alarm_does_not_exist(context, raw_name):
    alarm_found = is_alarm_present(context, raw_name)
    if alarm_found:
        name = format_alarm_name(context, raw_name)
        context.cloudwatch_client.delete_metric_alarms(name)


@given(u'VPCx managed alarm {raw_name} exists')
def alarm_exists(context, raw_name):
    alarm_found = is_alarm_present(context, raw_name)
    if not alarm_found:
        name = format_alarm_name(context, raw_name)
        default_alarm = {
            "MetricName": "TestingMetric",
            "Statistic": "Average",
            "Period": 300,
            "Namespace": "Testing",
            "EvaluationPeriods": 12,
            "Threshold": 95,
            "ComparisonOperator": "GreaterThanThreshold"
        }
        context.cloudwatch_client.create_metric_alarm(name, **default_alarm)


@then(u'API returns a status of {status}')
def check_return_status(context, status):
    assert_that(int(context.status_code), equal_to(int(status)))


@then(u'the response contains {message}')
def response_contains_message(context, message):
    try:
        error = context.response_data['error']
        assert_that(error, contains_string(message))
    except Exception as exc:
        logger.error(exc)
        assert False


@then(u'a cloudwatch alarm named {raw_name} is present')
def cloudwatch_alarm_present(context, raw_name):
    return is_alarm_present(context, raw_name)


@then(u'a cloudwatch alarm named {raw_name} is not present')
def cloudwatch_alarm_present(context, raw_name):
    return not is_alarm_present(context, raw_name)


def is_alarm_present(context, raw_name):
    name = format_alarm_name(context, raw_name)
    context.logger.info(f"Checking if alarm: {name} exists")
    alarm_found = context.cloudwatch_client.alarms_exist(AlarmNamePrefix=name)
    return alarm_found


def format_alarm_name(context, name):
    name = name.replace("<", "{")
    name = name.replace(">", "}")
    return name.format(ec2_hostname=context.hostname)


def invoke_api(context, method, local_func, extra={}):
    if context.run_behave_env != "LOCAL":
        logger.info(f"Invoking API {context.url}")
        headers = {
            'authorization': context.token,
            'Host': context.api_host
        }
        kwargs = {
            'headers': headers
        }
        kwargs.update(extra)
        response = requests.request(method, context.url, **kwargs)
        logger.info(response)
        context.response = response
        context.status_code = response.status_code
        context.response_data = json.loads(context.response.text)

    else:
        event_template = os.path.join(f"{SERVDIR}/common_bdd/events", "event.json")
        with open(event_template, "r") as read_file:
            event = json.load(read_file)
        url_params = context.url.split("/")
        event["headers"]["Authorization"] = context.token
        event["pathParameters"]["account_id"] = url_params[6]
        event["pathParameters"]["region_name"] = url_params[8]
        event["pathParameters"]["ec2_hostname"] = url_params[10]
        context.response = local_func(event, context)
        context.status_code = context.response["statusCode"]
        context.response_data = json.loads(context.response["body"])


def set_hostname(context, operating_system):
    logger.info("Updating url with valid instance")
    hostname = context.hostname_prefix.format(os=operating_system)
    context.hostname = hostname
    context.url = context.url.format(ec2_hostname=hostname)
    logger.info(context.url)
