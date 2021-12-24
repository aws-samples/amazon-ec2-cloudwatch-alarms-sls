@integration_test
@EC2-Alarms-API
@EC2-Provisioning

Feature: EC2 instance metric alarms

    Scenario Outline: Positive Scenario 1 - Success creating alarms
        Given PUT EC2 Alarms API exists
        And valid oauth2 token for API authorization generated
        And VPCx account is valid
        And Region is valid
        And <os> ec2 instance tagged with ec2_hostname running in the account
        And VPCx managed alarm itx-alarms-<ec2_hostname>-StatusCheckFailedFor10Mins <status>
        And VPCx managed alarm itx-alarms-<ec2_hostname>-CpuUtilizationGt95PercentFor60Mins <status>
        And VPCx managed alarm itx-alarms-<ec2_hostname>-MemoryUtilizationGt95PercentFor60Mins <status>
        When we invoke the api
        Then API returns a status of 200
        And a cloudwatch alarm named itx-alarms-<ec2_hostname>-StatusCheckFailedFor10Mins is present
        And a cloudwatch alarm named itx-alarms-<ec2_hostname>-CpuUtilizationGt95PercentFor60Mins is present
        And a cloudwatch alarm named itx-alarms-<ec2_hostname>-MemoryUtilizationGt95PercentFor60Mins is present
        And a cloudwatch alarm named itx-alarms-<ec2_hostname>-SwapspaceUtilizationGt95PercentFor60Mins is <linux_status>
    Examples: <os> instance with alarm status: <status>
        | os      | status         | linux_status |
        | windows | does not exist | not present  |
        | windows | exists         | not present  |
        | linux   | exists         | present      |
        | linux   | does not exist | present      |

    Scenario: Negative Scenario 1 - Invalid authorization token provided
        Given PUT EC2 Alarms API exists
        And invalid oauth2 token for API authorization generated
        When we invoke the api
        Then API returns a status of 401
        And the response contains UNAUTHORIZED (User/App Token Unauthorized)

    Scenario: Negative Scenario 2 - Invalid account ID provided
        Given PUT EC2 Alarms API exists
        And valid oauth2 token for API authorization generated
        And VPCx account is not valid
        When we invoke the api
        Then API returns a status of 404
        And the response contains Account not found

    Scenario: Negative Scenario 3 - Invalid region provided
        Given PUT EC2 Alarms API exists
        And valid oauth2 token for API authorization generated
        And VPCx account is valid
        And Region is not valid
        When we invoke the api
        Then API returns a status of 404
        And the response contains Region not found


    Scenario: Negative Scenario 4 - Invalid hostname provided
        Given PUT EC2 Alarms API exists
        And valid oauth2 token for API authorization generated
        And VPCx account is valid
        And Region is valid
        And instance not valid
        When we invoke the api
        Then API returns a status of 404