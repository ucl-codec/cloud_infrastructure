from typing import List

import aws_cdk.aws_logs as logs
from aws_cdk import RemovalPolicy, Environment
from aws_cdk import (
    aws_iam as iam,
    aws_efs as efs,
    Stack,
    aws_servicediscovery
)
from constructs import Construct
from aws_cdk.aws_ecr_assets import DockerImageAsset
from aws_cdk import (aws_ec2 as ec2, aws_ecs as ecs)
import aws_cdk.aws_ssm as ssm


class FbmBaseStack(Stack):

    def __init__(self, scope: Construct, construct_id: str, *,
                 stack_name: str,
                 stack_prefix: str,
                 description: str,
                 network_number: int,
                 cpu=8192,
                 memory_limit_mib=40960,
                 env: Environment) -> None:
        super().__init__(scope, construct_id,
                         stack_name=stack_name,
                         description=description,
                         env=env)

        self.stack_prefix = stack_prefix
        self.cidr_range = f"10.{2*network_number}.0.0/16"
        self.vpn_cidr_range = f"10.{2*network_number + 1}.0.0/22"
        self.dns_ip = f"10.{2*network_number}.0.2"
        self.vpn_cert_arn = ssm.StringParameter.value_for_string_parameter(
            self, "passian-fbm-vpn-server-cert-arn")

        # Create VPC
        self.vpc = ec2.Vpc(
            self,
            f"{self.stack_prefix}-VPC",
            # S3 gateway is required to use the ECR because we are using
            # a private subnet with no internet connectivity
            gateway_endpoints={
                "S3": ec2.GatewayVpcEndpointOptions(
                    service=ec2.GatewayVpcEndpointAwsService.S3
                )
            },
            cidr=self.cidr_range,
            nat_gateways=0,
            enable_dns_hostnames=True,
            enable_dns_support=True,
            max_azs=1,
            subnet_configuration=[
                ec2.SubnetConfiguration(
                    name="private",
                    cidr_mask=24,
                    subnet_type=ec2.SubnetType.PRIVATE_ISOLATED)]
            )

        # These endpoints are required in order to use the ECR and logging
        # because we are using a private subnet with no internet connectivity
        self.add_interface_endpoint(
            vpc=self.vpc,
            name=f"{self.stack_prefix}-FbmECRDockerEndpoint",
            service=ec2.InterfaceVpcEndpointAwsService.ECR_DOCKER)
        self.add_interface_endpoint(
            vpc=self.vpc,
            name=f"{self.stack_prefix}-FbmECREndpoint",
            service=ec2.InterfaceVpcEndpointAwsService.ECR)
        self.add_interface_endpoint(
            vpc=self.vpc,
            name=f"{self.stack_prefix}-FbmSecretManagerEndpoint",
            service=ec2.InterfaceVpcEndpointAwsService.SECRETS_MANAGER)
        self.add_interface_endpoint(
            vpc=self.vpc,
            name=f"{self.stack_prefix}-FbmCloudWatchEndpoint",
            service=ec2.InterfaceVpcEndpointAwsService.CLOUDWATCH)
        self.add_interface_endpoint(
            vpc=self.vpc,
            name=f"{self.stack_prefix}-FbmCloudWatchLogsEndpoint",
            service=ec2.InterfaceVpcEndpointAwsService.CLOUDWATCH_LOGS)
        self.add_interface_endpoint(
            vpc=self.vpc,
            name=f"{self.stack_prefix}-FbmCloudWatchEventsEndpoint",
            service=ec2.InterfaceVpcEndpointAwsService.CLOUDWATCH_EVENTS)
        self.add_interface_endpoint(
            vpc=self.vpc,
            name=f"{self.stack_prefix}-FbmSSMEndpoint",
            service=ec2.InterfaceVpcEndpointAwsService.SSM)

        # Create cluster
        self.cluster = ecs.Cluster(self, f"{self.stack_prefix}-Cluster",
                                   vpc=self.vpc)

        self.task_role = self.create_ecs_task_role()
        self.execution_role = self.create_ecs_execution_role()
        # Create Fargate task definition
        self.fargate_task_definition = ecs.FargateTaskDefinition(
            self,
            f"{self.stack_prefix}-FargateTaskDefinition",
            task_role=self.task_role,
            execution_role=self.execution_role,
            cpu=cpu,
            memory_limit_mib=memory_limit_mib,
            ephemeral_storage_gib=100
        )

        self.dns_namespace = None
        self.file_system = None
        self.vpn_endpoint = None

    def add_dns(self, namespace):

        # ToDo: Does not directly support discovery from peered VPC
        # You need to manually add the node VPC to the hosted zone that is
        # created here
        self.dns_namespace = aws_servicediscovery.PrivateDnsNamespace(
            self,
            f"{self.stack_prefix}-DnsNamespace",
            vpc=self.vpc,
            name=namespace,
            description="Private DnsNamespace for FBM"
        )

    def add_vpn(self):
        """Add VPN endpoint"""

        # ToDo: fetch server cert arn automatically
        self.vpn_endpoint = self.vpc.add_client_vpn_endpoint(
            f"{self.stack_prefix}-VpnEndpoint",
            cidr=self.vpn_cidr_range,
            server_certificate_arn=self.vpn_cert_arn,
            authorize_all_users_to_vpc_cidr=True,  # Automatically creates authorization rule
            client_certificate_arn=self.vpn_cert_arn,
            self_service_portal=False,
            split_tunnel=True,
            dns_servers=[self.dns_ip]
            # vpc_subnets=""
        )

    def add_volume(self, name: str, root_directory: str):
        volume_name = f"{self.stack_prefix}-{name}-volume"
        # Create access point first to force creation of directory in volume
        create_acl = efs.Acl(
            owner_uid="0",
            owner_gid="0",
            permissions="755"
        )
        access_point = efs.AccessPoint(
            self,
            f"{volume_name}AccessPoint",
            path=root_directory,
            file_system=self.file_system,
            create_acl=create_acl
        )
        self.fargate_task_definition.add_volume(
            name=volume_name,
            efs_volume_configuration=ecs.EfsVolumeConfiguration(
                file_system_id=self.file_system.file_system_id,
                root_directory='/',  # Note: relative to access point when using access_point_id
                transit_encryption="ENABLED",
                authorization_config=ecs.AuthorizationConfig(
                    access_point_id=access_point.access_point_id,
                    iam="ENABLED"
                )
            )
        )

        return volume_name

    def add_file_system(self):

        self.file_system = efs.FileSystem(
            self,
            f"{self.stack_prefix}-EfsFileSystem",
            vpc=self.vpc,
            removal_policy=RemovalPolicy.DESTROY,  # ToDo: change to persist
            # lifecycle_policy=efs.LifecyclePolicy.AFTER_7_DAYS,
            # files are not transitioned to infrequent access (IA) storage by default
            # performance_mode=efs.PerformanceMode.GENERAL_PURPOSE,
            # default
            # out_of_infrequent_access_policy=efs.OutOfInfrequentAccessPolicy.AFTER_1_ACCESS,
        )

    def add_docker_container(self, name, context_dir, path_to_dockerfile,
                             environment=None):
        """Run a Docker image as an ECR container using Fargate. The Docker
         image will be built locally as part of the cdk deploy and uploaded to
         the ECR"""
        environment = environment or {}
        docker_image = DockerImageAsset(
            self,
            id=f"{self.stack_prefix}-{name}",
            directory=context_dir,
            file=path_to_dockerfile
        )
        container = self.fargate_task_definition.add_container(
            f"{self.stack_prefix}-{name}Container",
            image=ecs.ContainerImage.from_docker_image_asset(docker_image),
            environment=environment,
            logging=ecs.LogDrivers.aws_logs(
                stream_prefix='{self.stack_prefix}-{name}-logs',
                log_retention=logs.RetentionDays.THREE_DAYS)
        )
        return container

    def add_service(self, dns_name: str, ports: List[int]):
        self.fargate_service = ecs.FargateService(
            self,
            f"{self.stack_prefix}-FargateService",
            cluster=self.cluster,
            desired_count=1,
            task_definition=self.fargate_task_definition,
            cloud_map_options=ecs.CloudMapOptions(
                name=dns_name,
                cloud_map_namespace=self.dns_namespace,
                dns_record_type=aws_servicediscovery.DnsRecordType.A
            ),
            service_name=f"{self.stack_prefix}-FargateServiceName"
        )
        if self.file_system:
            self.file_system.connections.allow_from(
                other=self.fargate_service,
                port_range=ec2.Port.tcp(2049),
                description='Allow access to file system from Fargate service')
        # self.file_system.connections.allow_default_port_from(self.fargate_service)
        for port in ports:
            self.fargate_service.connections.security_groups[0].add_ingress_rule(
                peer=ec2.Peer.ipv4(self.vpc.vpc_cidr_block),
                connection=ec2.Port.tcp(port),
                description=f"Allow http inbound from VPC on port {port}"
            )

    def add_interface_endpoint(self, vpc, name, service):
        endpoint = self.vpc.add_interface_endpoint(id=name, service=service)
        endpoint.connections.allow_from(ec2.Peer.ipv4(self.vpc.vpc_cidr_block),
                                        endpoint.connections.default_port)

    def create_ecs_execution_role(self):
        """Create IAM role to be used to create ECS tasks
        https://docs.aws.amazon.com/AmazonECS/latest/developerguide/task_execution_IAM_role.html
        """
        ecs_execution_role = iam.Role(self, f"{self.stack_prefix}-EcsExecutionRole",
            assumed_by=iam.ServicePrincipal("ecs-tasks.amazonaws.com"),
            role_name=f"{self.stack_prefix}-EcsExecutionRole"

                                    )
        ecs_execution_role.add_managed_policy(iam.ManagedPolicy.from_aws_managed_policy_name('AmazonEC2ContainerRegistryReadOnly'))
        ecs_execution_role.add_managed_policy(iam.ManagedPolicy.from_aws_managed_policy_name('CloudWatchLogsFullAccess'))
        ecs_execution_role.add_managed_policy(iam.ManagedPolicy.from_aws_managed_policy_name('AmazonElasticFileSystemReadOnlyAccess'))

        return ecs_execution_role

    def create_ecs_task_role(self):
        """Create IAM role to be used by the ECS tasks.
        https://docs.aws.amazon.com/AmazonECS/latest/developerguide/instance_IAM_role.html
        """
        ecs_task_role = iam.Role(self, f"{self.stack_prefix}-EcsTaskRole",
            assumed_by=iam.ServicePrincipal("ecs-tasks.amazonaws.com"),
            role_name=f"{self.stack_prefix}-EcsTaskRole"
        )

        ecs_task_role.add_managed_policy(iam.ManagedPolicy.from_aws_managed_policy_name('AmazonEC2ContainerRegistryReadOnly'))
        ecs_task_role.add_managed_policy(iam.ManagedPolicy.from_aws_managed_policy_name('CloudWatchLogsFullAccess'))
        ecs_task_role.add_managed_policy(iam.ManagedPolicy.from_aws_managed_policy_name('AmazonS3ReadOnlyAccess'))
        ecs_task_role.add_managed_policy(iam.ManagedPolicy.from_aws_managed_policy_name('AmazonElasticFileSystemFullAccess'))

        return ecs_task_role
