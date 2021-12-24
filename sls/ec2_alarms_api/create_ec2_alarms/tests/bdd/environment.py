import os
import sys

THISDIR = os.path.dirname(__file__)  # bdd/
TESTSDIR = os.path.dirname(THISDIR)  # tests/
LAMBDADIR = os.path.dirname(TESTSDIR)  # lambda_function/
SERVDIR = os.path.dirname(LAMBDADIR)  # ec2_alarms_api//
SLSDIR = os.path.dirname(SERVDIR)  # sls/
APPDIR = os.path.dirname(SLSDIR)  # ec2-provisioning/

sys.path.insert(0, THISDIR)
sys.path.insert(0, TESTSDIR)
sys.path.insert(0, LAMBDADIR)
sys.path.insert(0, SERVDIR)
sys.path.insert(0, SLSDIR)
sys.path.insert(0, APPDIR)

from ec2_alarms_api.common_bdd.environment import common_before_all
from ec2_alarms_api.common_bdd.alarms_setup import create_instances, delete_instances, delete_alarms


def before_all(context):
    common_before_all(context)
    context.ec2_instance_ids = []
    create_instances(context)


def after_all(context):
    delete_instances(context)
    delete_alarms(context)
