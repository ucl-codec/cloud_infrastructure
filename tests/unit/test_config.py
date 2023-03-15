from aws_fbm.utils.config import read_config_file, Config, NetworkConfig, \
    NodeConfig


def test_dev_config():
    """Test development stack configuration is correctly parsed"""
    config = read_config_file("dev")
    expected = Config(
        network=NetworkConfig(
            name_prefix="Test",
            site_name="Test Federated",
            domain_name="test.testfederated"
        ),
        nodes=[
            NodeConfig(
                name_prefix="TestA",
                stack_name="TestNodeStackA",
                site_name="Test Node A",
                domain_name="test.testclinicala",
                bucket_name="test-a-import-bucket"
            )
        ]
    )
    assert config == expected


def test_prod_config():
    """Test production stack configuration is correctly parsed"""
    config = read_config_file("prod")
    expected = Config(
        network=NetworkConfig(
            name_prefix="Fbm",
            site_name="Federated",
            domain_name="passian.federated"
        ),
        nodes=[
            NodeConfig(
                name_prefix="FbmNodeA",
                stack_name="FbmNodeStackA",
                site_name="Clinical Node A",
                domain_name="passian.clinicala",
                bucket_name="clinical-node-a-import-bucket"
            ),
            NodeConfig(
                name_prefix="FbmNodeB",
                stack_name="FbmNodeStackB",
                site_name="Clinical Node B",
                domain_name="passian.clinicalb",
                bucket_name="clinical-node-b-import-bucket"
            )
        ]
    )
    assert config == expected
