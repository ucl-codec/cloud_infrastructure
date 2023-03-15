from aws_fbm.utils.config import read_config_file


def test_dev_config():
    """Test development stack configuration is correctly parsed"""
    config = read_config_file("dev")
    assert config.network.name_prefix == "Test"
    assert config.network.site_name == "Test Federated"
    assert config.network.domain_name == "test.testfederated"
    assert len(config.nodes) == 1
    assert config.nodes[0].name_prefix == "TestA"
    assert config.nodes[0].stack_name == "TestNodeStackA"
    assert config.nodes[0].site_name == "Test Node A"
    assert config.nodes[0].domain_name == "test.testclinicala"
    assert config.nodes[0].bucket_name == "test-a-import-bucket"


def test_prod_config():
    """Test production stack configuration is correctly parsed"""
    config = read_config_file("prod")
    assert config.network.name_prefix == "Fbm"
    assert config.network.site_name == "Federated"
    assert config.network.domain_name == "passian.federated"
    assert len(config.nodes) == 2
    assert config.nodes[0].name_prefix == "FbmNodeA"
    assert config.nodes[0].stack_name == "FbmNodeStackA"
    assert config.nodes[0].site_name == "Clinical Node A"
    assert config.nodes[0].domain_name == "passian.clinicala"
    assert config.nodes[0].bucket_name == "clinical-node-a-import-bucket"
    assert config.nodes[1].name_prefix == "FbmNodeB"
    assert config.nodes[1].stack_name == "FbmNodeStackB"
    assert config.nodes[1].site_name == "Clinical Node B"
    assert config.nodes[1].domain_name == "passian.clinicalb"
    assert config.nodes[1].bucket_name == "clinical-node-b-import-bucket"
