"""
Contains behave step implementation
"""
# pylint: disable = import-error,no-name-in-module,C0413,missing-function-docstring,wrong-import-order

import os

from behave import when, given
from ec2_alarms_api.common_bdd import common_steps
from sls.ec2_alarms_api.delete_ec2_alarms.index import handler

THISDIR = os.path.dirname(__file__)  # steps/
BDD_DIR = os.path.dirname(THISDIR)  # bdd


@when(u'we invoke the api')
def invoke_api(context):
    common_steps.invoke_api(context, 'Delete', handler)


@given(u'hostname is set for instance')
def instance_running(context):
    common_steps.set_hostname(context, "windows")
