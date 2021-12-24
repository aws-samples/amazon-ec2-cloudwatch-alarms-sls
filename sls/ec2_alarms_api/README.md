# EC2 Alarms API

This API creates and deletes CloudWatch metric alarms for EC2 instances.

```
.
├── README.md                     <-- This documentation file
├── create_ec2_alarms             <-- Lambda function that creates alarms
├── delete_ec2_alarms             <-- Lambda function that deletes alarms
├── ec2-alarms-api.yaml           <-- Swagger doc 
└── serverless.yml                <-- Serverless application definition file
```

## Example Usage

```bash
# Create alarms for account-id=itx-000, in region=us-west-2 and for ec2_hostname=AWS000testing

curl -X PUT 
     -H 'Content-Type: application/json' 
     -H 'authorization: Bearer AMvcMSfZoAHnlXX0cAIhAKsJx8Pp' 
     -H 'Host': apiId.execute-api.us-east-1.amazonaws.com
     https://vpce-012710b591427fc69-kykwwlo6.execute-api.us-east-1.vpce.amazonaws.com/dev/v1/accounts/itx-000/regions/us-west-2/instances/AWS000testing/EC2Alarms


```
