# pylint: disable=missing-module-docstring, missing-function-docstring

import os

from sls.utils.aws_sm import SmClient
from sls.utils.aws_creds import AwsCreds
from sls.utils.api_request import ApiRequests


def set_env_variables(context, config, env_config):
    os.environ['token_url'] = config['ENVIRONMENT']['LDAP_TOKEN_URL']
    json_key_for_api_name = context.api_name.upper().replace("-", "_")
    os.environ['LDAP_GROUP_NAME'] = config[json_key_for_api_name]['LDAP_GROUP_NAME']
    os.environ["MSFT_IDP_CLIENT_ROLES"] = config[json_key_for_api_name]["MSFT_IDP_CLIENT_ROLES"]
    os.environ["MSFT_IDP_TENANT_ID"] = config["ENVIRONMENT"]["MSFT_IDP_TENANT_ID"]
    os.environ["APP_SECRET_NAME"] = config["ENVIRONMENT"]["APP_SECRET_NAME"]
    os.environ["AZURE_AUTH_CLIENT_ID"] = config["ENVIRONMENT"]["AZURE_AUTH_CLIENT_ID"]
    os.environ["AZURE_AUTH_SECRET_NAME"] = config["ENVIRONMENT"]["AZURE_AUTH_SECRET_NAME"]
    os.environ['vpcxiam_endpoint'] = env_config['VPCXIAM']['VPCXIAM_ENDPOINT']
    os.environ['vpcxiam_scope'] = env_config['VPCXIAM']['VPCXIAM_SCOPE']
    os.environ['vpcxiam_host'] = env_config['VPCXIAM']['VPCXIAM_HOST']
    os.environ['app_client_id'] = env_config['OAUTH2']['APP_CLIENT_ID']
    os.environ['main_account'] = env_config["MAIN"]["ACCOUNT"]
    os.environ["MSFT_IDP_APP_ID"] = env_config["MSFT"]["MSFT_IDP_APP_ID"]


def set_context(context, config, env_config, logger):
    context.token_url = config['ENVIRONMENT']['LDAP_TOKEN_URL']
    context.vpce_endpoint = env_config['VPCXIAM']['VPCXIAM_ENDPOINT']
    context.application_scope = env_config['OAUTH2']['APPLICATION_SCOPE']
    context.jenkins_client_id = env_config["BEHAVE"]["JENKINS_CLIENT_ID"]
    context.jenkins_secret_name = env_config["BEHAVE"]["JENKINS_SECRET_NAME"]
    #context.jenkins_client_id = env_config['OAUTH2']['APP_CLIENT_ID']
    #context.jenkins_secret_name = config["ENVIRONMENT"]["APP_SECRET_NAME"]
    context.run_behave_env = env_config["BEHAVE"]["BEHAVE_RUN_ENV"]
    context.admin_region = env_config['MAIN']['REGION']
    context.admin_account = env_config['MAIN']['ADMIN_ACCOUNT']
    context.main_account = env_config["MAIN"]["ACCOUNT"]
    context.main_region = env_config["BEHAVE"]["INSTANCE_REGION"]
    context.sg_name = env_config["BEHAVE"]["DB_VPC_SECURITY_GROUP_NAME"]
    context.subnet_name = env_config["BEHAVE"]["DB_SUBNET_GROUP_NAME"]
    context.subnet_id = env_config["BEHAVE"]["SUBNET_ID"]
    context.stack_name = f"{context.api_name}-{context.env}"
    context.admin_creds = AwsCreds(context.admin_account, logger)
    context.main_creds = AwsCreds(context.main_account, logger)
    context.api_req = ApiRequests()
    context.logger = logger


def set_jenkins_secret(context):
    sm_client = SmClient(aws_creds=context.admin_creds,
                         secret_region=context.admin_region,
                         logger=context.logger)
    context.jenkins_client_secret = sm_client.retrieve_secret(
        context.jenkins_secret_name
    )
