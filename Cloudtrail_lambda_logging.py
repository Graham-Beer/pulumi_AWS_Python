import pulumi
import json

from pulumi_aws import s3, cloudtrail
from pulumi import export

# Create s3 bucket for CloudTrail logging
bucket = s3.Bucket('cloudtrail-lambda')

# function to create bucket policy
def bucket_policy_cloudtrial(bucket_name):
    return json.dumps({
        "Version": "2012-10-17",
        "Statement": [
            {
                "Effect": "Allow",
                "Principal": {
                    "Service": "cloudtrail.amazonaws.com"
                },
                "Action": "s3:GetBucketAcl",
                "Resource": f"arn:aws:s3:::{bucket_name}"
            },
            {
                "Effect": "Allow",
                "Principal": {
                    "Service": "cloudtrail.amazonaws.com"
                },
                "Action": "s3:PutObject",
                "Resource": f"arn:aws:s3:::{bucket_name}/*",
                "Condition": {
                    "StringEquals": {
                        "s3:x-amz-acl": "bucket-owner-full-control"
                    }
                }
            }
        ]
    })

# apply policy to bucket
bucket_name = bucket.id
bucket_policy = s3.BucketPolicy(
    "bucket-policy",
    bucket = bucket_name,
    policy = bucket_name.apply(bucket_policy_cloudtrial)
    )

# Create cloudtrail for lambda's and write to s3 bucket
trail_lambda = cloudtrail.Trail(
    'CloudTrail logging for Lambda',
    enable_logging = 'true',
    name = "Cloudtrail_lambda",
    s3_bucket_name = bucket_name,
    event_selectors = [{
        'dataResources' : [{
           'type' : "AWS::Lambda::Function",
           'values' : [ "arn:aws:lambda" ]
        }],
        'includeManagementEvents' : True,
        'readWriteType' : "WriteOnly"
    }],
    tags = {'name': 'CloudTrail_lambda'}
    )
