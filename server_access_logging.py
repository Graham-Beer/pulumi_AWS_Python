import pulumi
from pulumi_aws import s3
from pulumi import export

# add new or existing bucket
bucket_name = ''
state = 'new' # or 'existing'

# New s3 bucket
if state == 'new':
    bucket_name = "server-access"
    bucket = s3.Bucket(
        bucket_name,
        acl = "log-delivery-write"
    )
# use existing server-access-log
elif state == 'existing':
    bucket = s3.Bucket.get("access-logs", bucket_name)

# apply server logging to new bucket
s3_logging = s3.Bucket(
    "cloudtrail-logs",
    acl = 'private',
    loggings = [{
        'targetBucket': bucket.id,
        'targetPrefix': "server_access_logging/"
    }]
)
