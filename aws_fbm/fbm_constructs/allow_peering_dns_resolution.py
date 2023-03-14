from constructs import Construct
from aws_cdk import aws_ec2 as ec2, aws_iam as iam, aws_logs as logs
from aws_cdk import custom_resources


class AllowVPCPeeringDNSResolution(Construct):

    def __init__(self, scope: Construct, id: str,
                 vpc_peering: ec2.CfnVPCPeeringConnection):
        super().__init__(scope, id)

        on_create = custom_resources.AwsSdkCall(
            service="EC2",
            action="modifyVpcPeeringConnectionOptions",
            parameters={
                "VpcPeeringConnectionId": vpc_peering.ref,
                "AccepterPeeringConnectionOptions": {
                    "AllowDnsResolutionFromRemoteVpc": True,
                },
                "RequesterPeeringConnectionOptions": {
                    "AllowDnsResolutionFromRemoteVpc": True
                }
            },
            physical_resource_id=custom_resources.PhysicalResourceId.of(
                'allowVPCPeeringDNSResolution:${props.vpcPeering.ref}'
            )
        )
        on_delete = custom_resources.AwsSdkCall(
            service="EC2",
            action="modifyVpcPeeringConnectionOptions",
            parameters={
                "VpcPeeringConnectionId": vpc_peering.ref,
                "AccepterPeeringConnectionOptions": {
                    "AllowDnsResolutionFromRemoteVpc": False,
                },
                "RequesterPeeringConnectionOptions": {
                    "AllowDnsResolutionFromRemoteVpc": False
                }
            }
        )

        custom_resource = custom_resources.AwsCustomResource(
            self, "AllowPeeringDnsResolution",
            policy=custom_resources.AwsCustomResourcePolicy.from_statements(
                statements=[
                    iam.PolicyStatement(
                        effect=iam.Effect.ALLOW,
                        resources=["*"],
                        actions=["ec2:ModifyVpcPeeringConnectionOptions"]
                    )
                ]),
            log_retention=logs.RetentionDays.ONE_DAY,
            on_create=on_create,
            on_update=on_create,
            on_delete=on_delete
        )
        custom_resource.node.add_dependency(vpc_peering)
