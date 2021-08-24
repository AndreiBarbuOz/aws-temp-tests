import boto3
import json
import cfnresponse
import threading
import uuid



def create(properties, physical_id):
    region = properties["RegionName"]
    autoscaling_name = properties["AutoScalingGroupName"]
    secret_arn = properties["TargetSecretArn"]
    db_password_secret_arn = properties["RDSPasswordSecretArn"]
    platform_secret_arn = properties['PlatformSecretArn']
    fqdn = properties["Fqdn"]
    db_endpoint = properties["RDSDBInstanceEndpointAddress"]
    total_node_count = int(properties["TotalNodeCount"])
    agent_count = int(properties["AgentCount"])

    ret = {"fqdn": fqdn, "rke_token": str(uuid.uuid4())}
    asg = boto3.client('autoscaling', region_name=region)
    response = asg.describe_auto_scaling_groups(
        AutoScalingGroupNames=[autoscaling_name]
    )
    print(response)
    instance_ids = [crt_elem["InstanceId"] for crt_elem in response["AutoScalingGroups"][0]["Instances"]]
    print(instance_ids)
    ec2 = boto3.client('ec2', region_name=region)
    ec2_descriptions = ec2.describe_instances(
        InstanceIds=instance_ids
    )
    print(ec2_descriptions)
    # clearer to explicitly iterate rather than nested list comprehensions
    reservations = []
    for crt_reservation in ec2_descriptions['Reservations']:
        reservations.append(crt_reservation)
    instances = []
    for crt_instance_group in reservations:
        instances.extend([crt_instance for crt_instance in crt_instance_group['Instances']])
    ips = [crt_vm["PrivateIpAddress"] for crt_vm in instances]
    print(ips)
    node_fqdns = [crt_vm["PrivateDnsName"] for crt_vm in instances]
    print(node_fqdns)
    if len(ips) < total_node_count:
        raise Exception("Cannot generate input.json file: insufficient node count")

    ret['server_ips'] = ips[:(total_node_count - agent_count)]
    ret['agent_ips'] = ips[(total_node_count - agent_count):]
    ret['fixed_rke_address'] = ips[0]
    ret['server_fqdns'] = node_fqdns[:(total_node_count - agent_count)]

    sm = boto3.client('secretsmanager', region_name=region)

    print("Getting Platform secret")
    db_secret = sm.get_secret_value(
        SecretId=platform_secret_arn
    )
    secret = json.loads(db_secret['SecretString'])
    print("Adding Platform username and password to JSON")
    ret["admin_username"] = secret['username']
    ret["admin_password"] = secret['password']

    print("Getting RDS secret")
    db_secret = sm.get_secret_value(
        SecretId=db_password_secret_arn
    )
    secret = json.loads(db_secret['SecretString'])
    connection_string = f"Server=tcp:{db_endpoint},1433;Initial Catalog=DB_NAME_PLACEHOLDER;Persist Security Info=False;User Id={secret['username']}@{db_endpoint};Password={secret['password']};MultipleActiveResultSets=False;Encrypt=True;TrustServerCertificate=False;Connection Timeout=30;Max Pool Size=100;"
    print("Adding SQL connection string to JSON")
    ret["sql_connection_string_template"] = connection_string

    sm.put_secret_value(
        SecretId=secret_arn,
        SecretString=json.dumps(ret)
    )
    return_attribute = dict()
    return cfnresponse.SUCCESS, secret_arn, return_attribute


def update(properties, physical_id):
    region = properties["RegionName"]
    autoscaling_name = properties["AutoScalingGroupName"]
    secret_arn = properties["TargetSecretArn"]
    db_password_secret_arn = properties["RDSPasswordSecretArn"]
    platform_secret_arn = properties['PlatformSecretArn']
    fqdn = properties["Fqdn"]
    db_endpoint = properties["RDSDBInstanceEndpointAddress"]
    total_node_count = int(properties["TotalNodeCount"])
    agent_count = int(properties["AgentCount"])

    ret = {"fqdn": fqdn, "rke_token": str(uuid.uuid4())}
    asg = boto3.client('autoscaling', region_name=region)
    response = asg.describe_auto_scaling_groups(
        AutoScalingGroupNames=[autoscaling_name]
    )
    print(response)
    instance_ids = [crt_elem["InstanceId"] for crt_elem in response["AutoScalingGroups"][0]["Instances"]]
    print(instance_ids)
    ec2 = boto3.client('ec2', region_name=region)
    ec2_descriptions = ec2.describe_instances(
        InstanceIds=instance_ids
    )
    print(ec2_descriptions)
    # clearer to explicitly iterate rather than nested list comprehensions
    reservations = []
    for crt_reservation in ec2_descriptions['Reservations']:
        reservations.append(crt_reservation)
    instances = []
    for crt_instance_group in reservations:
        instances.extend([crt_instance for crt_instance in crt_instance_group['Instances']])
    ips = [crt_vm["PrivateIpAddress"] for crt_vm in instances]
    print(ips)
    node_fqdns = [crt_vm["PrivateDnsName"] for crt_vm in instances]
    print(node_fqdns)
    if len(ips) < total_node_count:
        raise Exception("Cannot generate input.json file: insufficient node count")

    ret['server_ips'] = ips[:(total_node_count - agent_count)]
    ret['agent_ips'] = ips[(total_node_count - agent_count):]
    ret['fixed_rke_address'] = ips[0]
    ret['server_fqdns'] = node_fqdns[:(total_node_count - agent_count)]

    sm = boto3.client('secretsmanager', region_name=region)

    print("Getting Platform secret")
    db_secret = sm.get_secret_value(
        SecretId=platform_secret_arn
    )
    secret = json.loads(db_secret['SecretString'])
    print("Adding Platform username and password to JSON")
    ret["admin_username"] = secret['username']
    ret["admin_password"] = secret['password']

    print("Getting RDS secret")
    db_secret = sm.get_secret_value(
        SecretId=db_password_secret_arn
    )
    secret = json.loads(db_secret['SecretString'])
    connection_string = f"Server=tcp:{db_endpoint},1433;Initial Catalog=DB_NAME_PLACEHOLDER;Persist Security Info=False;User Id={secret['username']}@{db_endpoint};Password={secret['password']};MultipleActiveResultSets=False;Encrypt=True;TrustServerCertificate=False;Connection Timeout=30;Max Pool Size=100;"
    print("Adding SQL connection string to JSON")
    ret["sql_connection_string_template"] = connection_string

    sm.put_secret_value(
        SecretId=secret_arn,
        SecretString=json.dumps(ret)
    )
    return_attribute = dict()
    return_attribute['Action'] = 'UPDATE'
    return cfnresponse.SUCCESS, physical_id, return_attribute


def delete(properties, physical_id):
    return_attribute = {'Action': 'DELETE'}
    return cfnresponse.SUCCESS, physical_id, return_attribute


def timeout(event, context):
    print('Execution is about to time out, sending failure response to CloudFormation')
    cfnresponse.send(event, context, cfnresponse.FAILED, {}, None)


def handler(event, context):
    # make sure we send a failure to CloudFormation if the function is going to timeout
    # timer = threading.Timer((context.get_remaining_time_in_millis() / 1000.00) - 0.5, timeout, args=[event, context])
    # timer.start()
    print('Received event: ' + json.dumps(event))
    status = cfnresponse.FAILED
    new_physical_id = None
    returnAttribute = {}
    try:
        properties = event.get('ResourceProperties')
        physical_id = event.get('PhysicalResourceId')
        status, new_physical_id, returnAttribute = {
            'Create': create,
            'Update': update,
            'Delete': delete
        }.get(event['RequestType'], lambda x, y: (cfnresponse.FAILED, None))(properties, physical_id)
    except Exception as e:
        print('Exception: ' + str(e))
        status = cfnresponse.FAILED
    finally:
        print(returnAttribute)


if __name__ == '__main__':
    handler(request, None)
