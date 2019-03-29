#!/usr/bin/python3
import boto3, time, sys
from collections import Counter

# Select your profile and region
AWS_PROFILE='default'
AWS_REGION='eu-west-1'
boto3.setup_default_session(profile_name=AWS_PROFILE, region_name=AWS_REGION)

asg_client = boto3.client('autoscaling')
ecs_client = boto3.client('ecs')
alb_client = boto3.client('elbv2')

# Type here your vars
asg = "ASG name"
alb_target_group = 'Target group name'
arn = 'Target group ARN'


# build a list of current instance_ids, desired and max of asg
asg_response = asg_client.describe_auto_scaling_groups(AutoScalingGroupNames=[asg])
initial_ids = []
for i in asg_response['AutoScalingGroups']:
	for k in i['Instances']:
		initial_ids.append(k['InstanceId'])
for i in asg_response['AutoScalingGroups']:
	orig_maxsize = i['MaxSize']
	orig_desired = i['DesiredCapacity']


# double the size of the max and desired autoscaling group
new_maxsize = orig_maxsize*2
new_desired = orig_desired*2
double_size = asg_client.update_auto_scaling_group(
    AutoScalingGroupName=asg,
    MaxSize=new_maxsize,
    DesiredCapacity=new_desired,
)

# count autoscaling nodes currently 'InService'
def count_inservice():
	life_cycle = []
	asg_response = asg_client.describe_auto_scaling_groups(AutoScalingGroupNames=[asg])
	for i in asg_response['AutoScalingGroups']:
		for k in i['Instances']:
			life_cycle.append(k['LifecycleState'])
	ct= Counter(life_cycle)
	n = ct['InService']
	return(n)
	
	
# waiting on asg to double
x = count_inservice()
while x < new_desired:
	x = count_inservice()
	print(asg, 'nodes InService equals', x, 'waiting for it to reach', new_desired)
	time.sleep(5)


# giving some time to register new targets
time.sleep(140)

# drain old instances
for i in initial_ids:
	response = alb_client.deregister_targets(
    TargetGroupArn=arn,
    Targets=[
        {
            'Id': i,
        },
    ]
	)
	print('killing old instances \n', i,'\n', response)

# set this to alb timeout + 10, important: sleep for the amount your target group drain timeout is set
time.sleep(40)

# halfing asg size
print('reverting asg size, maxsize to', orig_maxsize, 'desired', orig_desired)
double_size = asg_client.update_auto_scaling_group(
    AutoScalingGroupName=asg,
    MaxSize=orig_maxsize,
    DesiredCapacity=orig_desired,
)

