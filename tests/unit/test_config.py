from aws_fbm.utils.config import read_config_file


def test_dev_config():
    config = read_config_file("dev")
    assert config.network.name_prefix == "Test"
    assert config.network.site_name == "Test Federated"
    assert config.network.domain_name == "test.testfederated"
    assert config.nodes[0].name_prefix == "TestA"
    assert config.nodes[0].stack_name == "TestNodeStackA"
    assert config.nodes[0].site_name == "Test Node A"
    assert config.nodes[0].domain_name == "test.testclinicala"
    assert config.nodes[0].bucket_name == "test-a-import-bucket"
