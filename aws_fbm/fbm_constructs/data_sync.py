from constructs import Construct
from aws_cdk import aws_ec2, aws_iam, aws_s3, aws_efs, aws_datasync
import aws_cdk.aws_logs as logs


class DataSync(Construct):
    """Set up automatic AWS DataSync from an existing S3 bucket to an EFS"""

    def __init__(
            self,
            scope: Construct,
            id: str,
            site_name: str,
            bucket_name: str,
            file_system: aws_efs.FileSystem,
            vpc: aws_ec2.Vpc,
            subnet_arn: str,
            region: str,
            account: str):
        super().__init__(scope, id)

        self.import_bucket = aws_s3.Bucket.from_bucket_name(
            scope=self, id="NodeImportBucket", bucket_name=bucket_name
        )

        # Create IAM role for accessing the S3 source bucket
        source_role = aws_iam.Role(
            self,
            id="DatasyncS3SourceAccessRole",
            assumed_by=aws_iam.ServicePrincipal("datasync.amazonaws.com")
        )
        source_role.add_to_principal_policy(
            statement=aws_iam.PolicyStatement(
                actions=[
                    "s3:GetBucketLocation",
                    "s3:ListBucket",
                    "s3:ListBucketMultipartUploads",
                    "s3:ListBucket",
                    "s3:ListObjectsV2"
                ],
                effect=aws_iam.Effect.ALLOW,
                resources=[self.import_bucket.bucket_arn]
            )
        )
        source_role.add_to_principal_policy(
            statement=aws_iam.PolicyStatement(
                actions=[
                    "s3:AbortMultipartUpload",
                    "s3:DeleteObject",
                    "s3:GetObject",
                    "s3:ListMultipartUploadParts",
                    "s3:PutObjectTagging",
                    "s3:GetObjectTagging",
                    "s3:PutObject",
                    "s3:ListBucket",
                    "s3:ListObjectsV2"
                ],
                effect=aws_iam.Effect.ALLOW,
                resources=[f"{self.import_bucket.bucket_arn}/*"]
            )
        )

        # Permit incoming connections from AWS DataSync to the S3 bucket
        self.import_bucket.grant_read(source_role)

        # Create the AWS DataSync source location
        source_location = aws_datasync.CfnLocationS3(
            self,
            "SourceLocation",
            s3_bucket_arn=self.import_bucket.bucket_arn,
            s3_config=aws_datasync.CfnLocationS3.S3ConfigProperty(
                bucket_access_role_arn=source_role.role_arn
            )
        )
        source_location.node.add_dependency(source_role)

        # Create IAM role for accessing the destination EFS bucket
        dest_efs_access_role = aws_iam.Role(
            self,
            id="DatasyncEfsDestinationAccessRole",
            assumed_by=aws_iam.ServicePrincipal("datasync.amazonaws.com")
        )
        dest_efs_access_role.add_managed_policy(
            aws_iam.ManagedPolicy.from_aws_managed_policy_name(
                'AWSDataSyncFullAccess'))

        # Create datasync security group
        datasync_security_group = aws_ec2.SecurityGroup(
            self,
            "DatasyncSecurityGroup",
            vpc=vpc,
            description='Datasync security group',
            allow_all_outbound=True,
        )
        dsg_arn = f'arn:aws:ec2:{region}:{account}:security-group/{datasync_security_group.security_group_id}'

        # Permit incoming connections from AWS DataSync to the EFS
        file_system.connections.allow_from(
            datasync_security_group,
            aws_ec2.Port.tcp(2049)
        )

        # Create the AWS DataSync destination location
        dest_location = aws_datasync.CfnLocationEFS(
            self,
            id="EfsDestinationLocation",
            ec2_config=aws_datasync.CfnLocationEFS.Ec2ConfigProperty(
                security_group_arns=[dsg_arn],
                subnet_arn=subnet_arn
            ),
            efs_filesystem_arn=file_system.file_system_arn,
            in_transit_encryption="TLS1_2",
            subdirectory='/node/data',
            tags=None)
        dest_location.node.add_dependency(file_system.mount_targets_available)

        self.log_group = logs.LogGroup(self, f"{site_name} data sync")

        # Create the DataSync task
        self.datasync_task = aws_datasync.CfnTask(
            self,
            id="DatasyncTask",
            destination_location_arn=dest_location.attr_location_arn,
            source_location_arn=source_location.attr_location_arn,
            cloud_watch_log_group_arn=self.log_group.log_group_arn,
            excludes=None,
            name=f"DataSync for {site_name}",
            options=aws_datasync.CfnTask.OptionsProperty(
                log_level="BASIC",
                preserve_deleted_files="REMOVE",
                transfer_mode="CHANGED",
                verify_mode="ONLY_FILES_TRANSFERRED"
            ),
            schedule=aws_datasync.CfnTask.TaskScheduleProperty(
                schedule_expression="cron(0 0 * ? * * *)"
            ),
            tags=None)
