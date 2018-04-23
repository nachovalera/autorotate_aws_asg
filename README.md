# AUTOROTATE-AWS-ASG
Recycle ami's and User Data in an ASG gracefully
# Use cases
You do run an ASG in aws on a set of ec2 ami's which need to be recycled gracefully (production servers)
(new OS ver, updated yum packages, new source ami, new ssh keys, etc).
# How to run it
Edit autorotate.py with your AWS_PROFILE (defined in ~/.aws/credentials), your region, your asg name and the TG arn. 
<pre>python autorotate.py</pre>

# What it does
It will double your autoscaling service count temporary, and once they equalize, drain the old instances, reduce the ASG back to initial, and restore autoscaling desired and max counts. Due to the oldestinstance term policy, autoscaling will terminate your previous instances.
