import pulumi
from pulumi import Output, ResourceOptions, export
from pulumi_aws import s3, ec2

# create bucket for VPC logs
bucket_vpc_and_subnets = s3.Bucket(
    'vpc-and-subnet-flow-logs',
    force_destroy = True
)

# s3 Block Public access
s3.BucketPublicAccessBlock(
    f"Block_Public_access",
    block_public_acls = True,
    block_public_policy = True,
    ignore_public_acls = True,
    restrict_public_buckets = True,
    bucket = bucket_vpc_and_subnets.id
)

# Find VPC information
vpcs = ec2.get_vpcs().ids

for vpc in vpcs:
    ec2.FlowLog(
        f"flowlogs_{vpc}",
        opts = ResourceOptions(
            depends_on = [
                bucket_vpc_and_subnets
        ]),
        log_destination = bucket_vpc_and_subnets.arn,
        log_destination_type = 's3',
        traffic_type = 'ALL',
        vpc_id = vpc
    )
