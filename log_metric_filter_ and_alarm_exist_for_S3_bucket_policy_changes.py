import pulumi, json
from pulumi import Output, ResourceOptions
from pulumi_aws import(
    s3,
    cloudtrail,
    cloudwatch,
    iam
)

# region and account ID
region = 'eu-west-2'
account_id = ''

# Create s3 bucket for CloudTrail logging
bucket = s3.Bucket(
    'cloudtrail-s3',
    force_destroy = True
)

# function to create bucket policy
def bucket_policy_cloudtrial(bucket_name):
    return json.dumps({
        "Version": "2012-10-17",
        "Statement": [
            {
                "Sid": "AWSCloudTrailAclCheck",
                "Effect": "Allow",
                "Principal": {
                    "Service": "cloudtrail.amazonaws.com"
                },
                "Action": "s3:GetBucketAcl",
                "Resource": f"arn:aws:s3:::{bucket_name}"
            },
            {
                "Sid": "AWSCloudTrailWrite",
                "Effect": "Allow",
                "Principal": {
                    "Service": "cloudtrail.amazonaws.com"
                },
                "Action": "s3:PutObject",
                "Resource": f"arn:aws:s3:::{bucket_name}/prefix/AWSLogs/{account_id}/*",
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

# s3 Block Public access
s3Access = s3.BucketPublicAccessBlock(
    "Block Public access",
    block_public_acls = True,
    block_public_policy = True,
    ignore_public_acls = True,
    restrict_public_buckets = True,
    bucket = bucket.id
)

# Create cloudwatch log
cloudwatch_log = cloudwatch.LogGroup(
    'LogGroup',
    name = 'S3BucketActivity'
)

# add log stream to cloudwatch log
log_stream = cloudwatch.LogStream(
    "CloudWatch_log_stream",
    log_group_name = cloudwatch_log.name,
    name = '818155059458_CloudTrail_eu-west-2'
)

# configure cloudwatch metrics
cloudwatch_metrics = cloudwatch.LogMetricFilter(
    'Metrics',
    log_group_name = cloudwatch_log.name,
    metric_transformation = {
        'name': "S3Activity",
        'namespace': "S3ActivityEventCount",
        'value': "1"
    },
    pattern = "{ ($.eventSource = s3.amazonaws.com) && (($.eventName = PutBucketAcl) || ($.eventName = PutBucketPolicy) || ($.eventName = PutBucketCors) || ($.eventName = PutBucketLifecycle) || ($.eventName = PutBucketReplication) || ($.eventName = DeleteBucketPolicy) || ($.eventName = DeleteBucketCors) || ($.eventName = DeleteBucketLifecycle) || ($.eventName = DeleteBucketReplication)) }"
)

# Create role for cloudtrail service
role = iam.Role(
    "cloudwatch_log_stream_role",
    assume_role_policy = json.dumps({
        "Version": "2012-10-17",
        "Statement": [{
            "Action": "sts:AssumeRole",
            "Principal": {
                "Service": "cloudtrail.amazonaws.com"
            },
            "Effect": "Allow",
            "Sid": ""
        }]
    }))

# function to create role policy JSON code
def iam_role_generate(resource):
    return json.dumps({
        "Version": "2012-10-17",
        "Statement": [
        {
            "Sid": "AWSCloudTrailCreateLogStream",
            "Effect": "Allow",
            "Action": ["logs:CreateLogStream"],
            "Resource": f"{resource}"
        },
        {
            "Sid": "AWSCloudTrailPutLogEvents",
            "Effect": "Allow",
            "Action": ["logs:PutLogEvents"],
            "Resource": f"{resource}"
        }]
    })

# build resource string for iam_role_generate function
resource = Output.concat(
    "arn:aws:logs:",region,
    ":",
    account_id,
    ":log-group:",
    cloudwatch_log.name,
    ":log-stream:",
    log_stream.name,
    "*"
)

# Apply policy to role
role_policy = iam.RolePolicy(
   "cloudwatch_log_stream",
    role = role.id,
    policy = resource.apply(iam_role_generate)
)

# Create cloudtrail for s3 and write to s3 bucket
trail_s3 = cloudtrail.Trail(
    'CloudTrail_logging_for_s3',
    opts = ResourceOptions(depends_on = [
        bucket_policy
    ]),
    cloud_watch_logs_group_arn = cloudwatch_log.arn,
    cloud_watch_logs_role_arn = role.arn,
    enable_logging = True,
    enable_log_file_validation = True,
    name = "Cloudtrail_s3",
    s3_bucket_name = bucket.id,
    s3_key_prefix = 'prefix',
    is_multi_region_trail = True,
    event_selectors = [{
        "dataResources" : [{
           "type" : "AWS::S3::Object",
           "values" : [
               "arn:aws:s3"
            ]
        }],
        "includeManagementEvents" : True,
        "readWriteType" : "All"
    }],
    tags = {
        'name': 'CloudTrail_s3'
    }
)
