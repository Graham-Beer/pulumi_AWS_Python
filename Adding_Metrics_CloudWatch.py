import pulumi
from pulumi_aws import s3, cloudwatch

cw_log = cloudwatch.get_log_group(name = 'S3BucketActivity')

metrics = {}
metrics['SecurityGroupChangesMetricFilter'] = {}
metrics['NetworkAclChangesMetricFilter'] = {}
metrics['GatewayChangesMetricFilter'] = {}
metrics['VpcChangesMetricFilter'] = {}
metrics['EC2InstanceChangesMetricFilter'] = {}
metrics['EC2LargeInstanceChangesMetricFilter'] = {}
metrics['CloudTrailChangesMetricFilter'] = {}
metrics['ConsoleSignInFailuresMetricFilter'] = {}
metrics['AuthorizationFailuresMetricFilter'] = {}
metrics['IAMPolicyChangesMetricFilter'] = {}
metrics['AWSConfigChangesMetricFilter'] = {}
metrics['S3BucketChangesMetricFilter'] = {}
metrics['RootChangesMetricFilter'] = {}
metrics['RouteTableChangesMetricFilter'] = {}
metrics['NomfaConsoleLoginsChangesMetricFilter'] = {}

metrics['SecurityGroupChangesMetricFilter']['pattern'] = '{( \
    ($.eventName = AuthorizeSecurityGroupIngress) \
    || ($.eventName = AuthorizeSecurityGroupEgress) || ($.eventName = RevokeSecurityGroupIngress) \
    || ($.eventName = RevokeSecurityGroupEgress) || ($.eventName = CreateSecurityGroup) \
    || ($.eventName = DeleteSecurityGroup) )}'
metrics['NetworkAclChangesMetricFilter']['pattern'] = '{( \
    ($.eventName = CreateNetworkAcl) || ($.eventName = CreateNetworkAclEntry) || ($.eventName = DeleteNetworkAcl) \
    || ($.eventName = DeleteNetworkAclEntry) || ($.eventName = ReplaceNetworkAclEntry) \
    || ($.eventName = ReplaceNetworkAclAssociation) )}'
metrics['GatewayChangesMetricFilter']['pattern'] = '{( \
    ($.eventName = CreateCustomerGateway) || ($.eventName = DeleteCustomerGateway) || \
    ($.eventName = AttachInternetGateway) || ($.eventName = CreateInternetGateway) \
    || ($.eventName = DeleteInternetGateway) || ($.eventName = DetachInternetGateway) )}'
metrics['VpcChangesMetricFilter']['pattern'] = '{( \
    ($.eventName = CreateVpc) || ($.eventName = DeleteVpc) || ($.eventName = ModifyVpcAttribute) \
    || ($.eventName = AcceptVpcPeeringConnection) || ($.eventName = CreateVpcPeeringConnection) \
    || ($.eventName = DeleteVpcPeeringConnection) || ($.eventName = RejectVpcPeeringConnection) \
    || ($.eventName = AttachClassicLinkVpc) || ($.eventName = DetachClassicLinkVpc) \
    || ($.eventName = DisableVpcClassicLink) || ($.eventName = EnableVpcClassicLink) )}'
metrics['EC2InstanceChangesMetricFilter']['pattern'] = '{( \
    ($.eventName = RunInstances) || ($.eventName = RebootInstances) || ($.eventName = StartInstances) \
    || ($.eventName = StopInstances) || ($.eventName = TerminateInstances) )}'
metrics['EC2LargeInstanceChangesMetricFilter']['pattern'] = '{( \
    ($.eventName = RunInstances) && (($.requestParameters.instanceType = *.8xlarge) \
    || ($.requestParameters.instanceType = *.4xlarge)) )}'
metrics['CloudTrailChangesMetricFilter']['pattern'] = '{( \
    ($.eventName = CreateTrail) || ($.eventName = UpdateTrail) || ($.eventName = DeleteTrail) \
    || ($.eventName = StartLogging) || ($.eventName = StopLogging) )}'
metrics['ConsoleSignInFailuresMetricFilter']['pattern'] = '{( \
    ($.eventName = ConsoleLogin) && ($.errorMessage = "Failed authentication") )}'
metrics['AuthorizationFailuresMetricFilter']['pattern'] = '{( \
    ($.errorCode = "*UnauthorizedOperation") || ($.errorCode = "AccessDenied*") )}'
metrics['IAMPolicyChangesMetricFilter']['pattern'] = '{( ($.eventName=DeleteGroupPolicy)||($.eventName=DeleteRolePolicy)||($.eventName=DeleteUserPolicy)||($.eventName=PutGroupPolicy)||($.eventName=PutRolePolicy)||($.eventName=PutUserPolicy)||($.eventName=CreatePolicy)||($.eventName=DeletePolicy)||($.eventName=CreatePolicyVersion)||($.eventName=DeletePolicyVersion)||($.eventName=AttachRolePolicy)||($.eventName=DetachRolePolicy)||($.eventName=AttachUserPolicy)||($.eventName=DetachUserPolicy)||($.eventName=AttachGroupPolicy)||($.eventName=DetachGroupPolicy) )}'
metrics['AWSConfigChangesMetricFilter']['pattern'] = '{( \
    $.eventSource=config.amazonaws.com) && (($.eventName=StopConfigurationRecorder) || ($.eventName=DeleteDeliveryChannel) \
    || ($.eventName=PutDeliveryChannel) || ($.eventName=PutConfigurationRecorder) )}'
metrics['S3BucketChangesMetricFilter']['pattern'] = '{( \
    ($.eventSource = s3.amazonaws.com) && (($.eventName = PutBucketAcl) || ($.eventName = PutBucketPolicy) || ($.eventName = PutBucketCors) || \
     ($.eventName = PutBucketLifecycle) || ($.eventName = PutBucketReplication) || ($.eventName = DeleteBucketPolicy) || ($.eventName = \
     DeleteBucketCors) || ($.eventName = DeleteBucketLifecycle) || ($.eventName = DeleteBucketReplication)) )}'
metrics['RootChangesMetricFilter']['pattern'] = '{( \
    $.userIdentity.type = "Root" && $.userIdentity.invokedBy NOT EXISTS && $.eventType != "AwsServiceEvent" )}'
metrics['RouteTableChangesMetricFilter']['pattern'] = '{( \
    ($.eventName = AssociateRouteTable) || ($.eventName = CreateRoute) || ($.eventName = CreateRouteTable) || ($.eventName = DeleteRoute) \
    || ($.eventName = DeleteRouteTable) || ($.eventName = ReplaceRoute) || ($.eventName = ReplaceRouteTableAssociation) \
    || ($.eventName = DisassociateRouteTable) )}'
metrics['NomfaConsoleLoginsChangesMetricFilter']['pattern'] = '{( \
    ($.eventName = "ConsoleLogin") && ($.additionalEventData.MFAUsed !="Yes") && ($.responseElements.ConsoleLogin != "Failure") && \
    ($.additionalEventData.SamlProviderArn NOT EXISTS) )}'

# Apply metrics
for metricName in metrics:
    cloudwatch.LogMetricFilter(
        metricName,
        log_group_name = cw_log.name,
        metric_transformation = {
            'name': f"{metricName}",
            'namespace': "{}Event".format(metricName),
            'value': "1"
        },
        pattern = metrics[metricName]['pattern']
    )
