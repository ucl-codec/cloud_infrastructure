from constructs import Construct
from aws_cdk import aws_ec2, aws_efs, RemovalPolicy


class FbmVolume(Construct):
    """A volume to be stored within a FbmFileSystem.
     The root directory specified where in the file system the volume contents
     will be stored. This directory will be created if it does not exist"""

    def __init__(self,
                 scope: Construct,
                 name: str,
                 file_system: aws_efs.FileSystem,
                 root_directory: str,
                 mount_dir: str):
        super().__init__(scope=scope, id=name)
        self.volume_name = name
        self.file_system_id = file_system.file_system_id
        self.mount_dir = mount_dir

        # Creating access point will force creation of directory in volume
        # This is necessary otherwise mounting the volume will fail if the
        # directory does not exist
        create_acl = aws_efs.Acl(
            owner_uid="0",
            owner_gid="0",
            permissions="755"
        )
        self.access_point = aws_efs.AccessPoint(
            scope=self,
            id="AccessPoint",
            path=root_directory,
            file_system=file_system,
            create_acl=create_acl
        )


class FbmFileSystem(Construct):
    """An ECS file system which may host multiple volumes"""

    def __init__(self, scope: Construct, id: str, vpc: aws_ec2.Vpc):
        super().__init__(scope=scope, id=id)

        self.file_system = aws_efs.FileSystem(
            self,
            "EfsFileSystem",
            vpc=vpc,
            removal_policy=RemovalPolicy.DESTROY,  # ToDo: change to persist
            # lifecycle_policy=efs.LifecyclePolicy.AFTER_7_DAYS,
            # files are not transitioned to infrequent access (IA) storage by
            # default
            # performance_mode=efs.PerformanceMode.GENERAL_PURPOSE,
            # default
            # out_of_infrequent_access_policy=
            #   efs.OutOfInfrequentAccessPolicy.AFTER_1_ACCESS,
        )

    def create_volume(self, name: str, root_directory: str, mount_dir: str):
        return FbmVolume(scope=self,
                         name=name,
                         file_system=self.file_system,
                         root_directory=root_directory,
                         mount_dir=mount_dir)
