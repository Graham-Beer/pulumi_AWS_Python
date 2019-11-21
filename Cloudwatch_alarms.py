import pulumi
from pulumi_aws import s3, cloudwatch

alarms = {}
alarms['SecurityGroupChangesAlarm'] = {}
alarms['NetworkAclChangesAlarm'] = {}
alarms['GatewayChangesAlarm'] = {}
alarms['VpcChangesAlarm'] = {}
alarms['EC2InstanceChangesAlarm'] = {}
alarms['EC2LargeInstanceChangesAlarm'] = {}
alarms['CloudTrailChangesAlarm'] = {}
alarms['ConsoleSignInFailuresAlarm'] = {}
alarms['AuthorizationFailuresAlarm'] = {}
alarms['IAMPolicyChangesAlarm'] = {}
alarms['AWSConfigChangesMetricAlarm'] = {}
alarms['S3BucketChangesMetricAlarm'] = {}
alarms['RootChangesMetricAlarm'] = {}
alarms['RouteTableChangesMetricAlarm'] = {}
alarms['NomfaConsoleLoginsChangesAlarm'] = {}

# changes
alarms['ConsoleSignInFailuresAlarm']['threshold'] = 3

for alarm in alarms:
    alarmName = alarm.split('Changes')

    if 'threshold' in alarms[alarm]:
        threshold = alarms[alarm]['threshold']
    else:
        threshold = 1

    cloudwatch.MetricAlarm(
        alarm,
        alarm_actions = None,
        alarm_description = f"Alarms when an API call is made to create, update or delete a {alarmName[0]}.",
        name = alarm,
        comparison_operator = "GreaterThanOrEqualToThreshold",
        statistic = "Sum",
        evaluation_periods = 1,
        metric_name = f"{alarmName}EventCount",
        namespace = f"{alarmName}Metrics",
        period = 300,
        threshold = threshold
    )
