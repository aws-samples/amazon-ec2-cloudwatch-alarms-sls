# EC2 CloudWatch Alarms API
This project creates a centralized API for creating/deleting EC2 CloudWatch alarms on EC2 Instance Metrics in a multi-account AWS Organizations implementation.
CloudWatch Alarms can be created/deleted by the API on following EC2 metrics:
 * PartitionUtilization (Namespace: System/Windows. Custom metrics that tracks disk partition utilization.)
 * StatusCheckFailed (Namespace: AWS/EC2. Reports whether the instance has passed both the instance status check and the system status check in the last minute.)
 * CPUUtilization (Namespace: AWS/EC2. default AWS metric that tracks CPU utilization on the EC2 instance)
 * MemoryUtilization (Namespace: System/Windows, System/Linux. Custom metrics that tracks memory utilization.)
 * SwapUtilization (Namespace: System/Linux. Custom metrics that tracks swap space utilization.)
 * DiskSpaceUtilization (Namespace: System/Linux. Custom metrics that tracks disk space utilization.)

The alarm will send notifications to the CloudWatch alarm SNS topic in the account.
Every account has Alarms SNS topic created by VPCx automation that is configured to send the received message to a SQS queue in central account. 

## Architecture
![Architecture2](docs/arch.png)

## Directory structure
```
.
├── README.md                     <-- This documentation file
├── config                        <-- Configuration files for the app
├── ec2_alarms_api                <-- Service that creates tags for EC2 instances
├── scripts                       <-- Deployment scripts
├── utils                         <-- Functions shared by multiple services
├── package.json                  <-- Serverless frameowrk dependencies
└── requirements.txt              <-- Python dependencies
```
---
## Local env setup

```
pip3 install -r requirements.txt
```
---
## Test
```shell script
pytest ./
```
----
## Deployment
```
serverless deploy -s dev
```
----
## BDD Integration Tests

```
behave sls/ec2_alarms_api/create_ec2_alarms/tests/bdd/
behave sls/ec2_alarms_api/delete_ec2_alarms/tests/bdd/
```

## License
This library is licensed under the MIT-0 License. See the LICENSE file.