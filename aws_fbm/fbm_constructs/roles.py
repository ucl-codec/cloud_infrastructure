from constructs import Construct

from aws_cdk import aws_iam as iam


class EcsExecutionRole(iam.Role):
    """IAM role to be used to create ECS tasks"""
    def __init__(self, scope: Construct):
        super().__init__(
            scope=scope,
            id="EcsExecutionRole",
            assumed_by=iam.ServicePrincipal("ecs-tasks.amazonaws.com"))
        self.add_managed_policy(iam.ManagedPolicy.from_aws_managed_policy_name(
            'AmazonEC2ContainerRegistryReadOnly'))
        self.add_managed_policy(iam.ManagedPolicy.from_aws_managed_policy_name(
            'CloudWatchLogsFullAccess'))
        self.add_managed_policy(iam.ManagedPolicy.from_aws_managed_policy_name(
            'AmazonElasticFileSystemReadOnlyAccess'))


class EcsTaskRole(iam.Role):
    """IAM role to be used by ECS tasks"""

    def __init__(self, scope: Construct):
        super().__init__(
            scope=scope,
            id="EcsTaskRole",
            assumed_by=iam.ServicePrincipal("ecs-tasks.amazonaws.com"))
        self.add_managed_policy(iam.ManagedPolicy.from_aws_managed_policy_name(
            'AmazonEC2ContainerRegistryReadOnly'))
        self.add_managed_policy(iam.ManagedPolicy.from_aws_managed_policy_name(
            'CloudWatchLogsFullAccess'))
        self.add_managed_policy(iam.ManagedPolicy.from_aws_managed_policy_name(
            'AmazonS3ReadOnlyAccess'))
        self.add_managed_policy(iam.ManagedPolicy.from_aws_managed_policy_name(
            'AmazonElasticFileSystemFullAccess'))


class Ec2LaunchRole(iam.Role):
    """IAM role to be used to launch EC2 instances"""

    def __init__(self, scope: Construct):
        super().__init__(
            scope=scope,
            id="Ec2LaunchRole",
            assumed_by=iam.ServicePrincipal("ec2.amazonaws.com"))
        self.add_managed_policy(iam.ManagedPolicy.from_aws_managed_policy_name(
                'service-role/AmazonEC2ContainerServiceforEC2Role'))
        self.add_managed_policy(
            iam.ManagedPolicy.from_aws_managed_policy_name(
                'AmazonSSMManagedInstanceCore'))
