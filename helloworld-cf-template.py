"""Generating CloudFormation Template."""

# Import libraries:
from ipaddress import ip_network
from ipify import get_ip

# Import definitions from tropo modules
from troposphere import (
        Base64,
        ec2,
        GetAtt,
        Join, 
        Output,
        Parameter,
        Ref,
        Template,
)

# Define web port for example scripts
ApplicationPort = "3000"

# Get public IP and save to variable
PublicCidrIp = str(ip_network(get_ip()))

# Define template variable
t = Template()

# Template description
t.add_description("Effective DevOps in AWS: HelloWorld Web App")

# Get KeyPair
t.add_parameter(Parameter(
        "KeyPair",
        Description="Name of an existing EC2 KeyPair to SSH",
        Type="AWS::EC2::KeyPair::KeyName", 
        ConstraintDescription="Must be the name of an existing EC2 KeyPair.",
))

# Create Security Group
t.add_resource(ec2.SecurityGroup(
        "SecurityGroup",
        GroupDescription="Allow SSH and TCP/{} access".format(ApplicationPort),
        SecurityGroupIngress=[
                ec2.SecurityGroupRule(
                        IpProtocol="tcp",
                        FromPort="22",
                        ToPort="22",
                        CidrIp=PublicCidrIp,
                ),
                ec2.SecurityGroupRule(
                        IpProtocol="tcp",
                        FromPort=ApplicationPort,
                        ToPort=ApplicationPort,
                        CidrIp=PublicCidrIp,
                ),
        ],
))

# Automate the helloworld.js installation
ud = Base64(Join('\n', [
        "#!/bin/bash",
        "sudo yum install --enablerepo=epel -y nodejs",
        "wget http://bit.ly/2vESNuc -O /home/ec2-user/helloworld.js",
        "wget http://bit.ly/2vVvT18 -O /etc/init/helloworld.conf",
        "start helloworld"
]))

# Create ec2 instance and install helloworld
t.add_resource(ec2.Instance(
        "instance",
        ImageId="ami-0ad99772",
        InstanceType="t2.micro",
        SecurityGroups=[Ref("SecurityGroup")],
        KeyName=Ref("KeyPair"),
        UserData=ud,
))

# Get the info from the instance
t.add_output(Output(
        "InstancePublicIp",
        Description="Public IP of our instance.",
        Value=GetAtt("instance", "PublicIp"),
))

t.add_output(Output(
        "WebUrl",
        Description="Application end-point",
        Value=Join("", [
                "http://", GetAtt("instance", "PublicDnsName"),
                ":", ApplicationPort
        ])
))

# Print output
print t.to_json()




