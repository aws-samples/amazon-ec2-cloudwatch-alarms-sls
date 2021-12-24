"""
Contains behave step implementation
"""
# pylint: disable = import-error,no-name-in-module,C0413,missing-function-docstring,wrong-import-order

import os

from behave import when, given
from ec2_alarms_api.common_bdd import common_steps
from sls.ec2_alarms_api.create_ec2_alarms.index import handler

THISDIR = os.path.dirname(__file__)  # steps/
BDD_DIR = os.path.dirname(THISDIR)  # bdd


@when(u'we invoke the api')
def invoke_api(context):
    common_steps.invoke_api(context, 'PUT', handler)


@given(u'{operating_system} ec2 instance tagged with ec2_hostname running in the account')
def instance_running(context, operating_system):
    common_steps.set_hostname(context, operating_system)
