import pulumi
from pulumi_aws import s3, ec2

# create bucket for VPC logs
bucket = s3.Bucket('vpc-flow-logs')

# Find VPC information
vpc = ec2.get_vpc()

vpcConfig = ec2.FlowLog(
    'flowlogs',
    log_destination = bucket.arn,
    log_destination_type = 's3',
    traffic_type = 'ALL',
    vpc_id = vpc.id
)

# create bucket for subnet logs
bucket2 = s3.Bucket('subnet-flow-logs')

# list of subnets
if len(str(vpc.id).split()) > 1:
    subnet_ids = []
    for net in vpc.id:
        subnet_ids.append(ec2.get_subnet_ids(vpc_id = net).ids)
else:
   subnet_ids = ec2.get_subnet_ids(vpc_id = vpc.id).ids

# Config log for each subnet
for id in subnet_ids:
    subnet_logs = ec2.FlowLog(
        f'subnetlogs_{id}',
        log_destination = bucket2.arn,
        log_destination_type = 's3',
        traffic_type = 'ALL',
        subnet_id = id
    )

# pulumi up --yes
# pulumi stack export > logging.json
