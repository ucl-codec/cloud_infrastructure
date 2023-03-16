import configparser
from dataclasses import dataclass

from aws_fbm.utils.config import read_config_file, Config, NetworkConfig, \
    NodeConfig, parse_config, convert_inputs, convert_to


def test_dev_config():
    """Test development stack configuration is correctly parsed"""
    config = read_config_file("dev")
    expected = Config(
        network=NetworkConfig(
            name_prefix="Test",
            site_name="Test Federated",
            domain_name="test.testfederated",
            vpn_cert_arn_param_name="passian-fbm-vpn-server-cert-arn"
        ),
        nodes=[
            NodeConfig(
                name_prefix="TestA",
                stack_name="TestNodeStackA",
                site_name="Test Node A",
                domain_name="test.testclinicala",
                bucket_name="test-a-import-bucket",
                enable_training_plan_approval=True,
                allow_default_training_plans=False,
                use_production_gui=True,
                vpn_cert_arn_param_name="passian-fbm-vpn-server-cert-arn"
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
            domain_name="passian.federated",
            vpn_cert_arn_param_name="passian-fbm-vpn-server-cert-arn"
        ),
        nodes=[
            NodeConfig(
                name_prefix="FbmNodeA",
                stack_name="FbmNodeStackA",
                site_name="Clinical Node A",
                domain_name="passian.clinicala",
                bucket_name="clinical-node-a-import-bucket",
                enable_training_plan_approval=True,
                allow_default_training_plans=False,
                use_production_gui=False,
                vpn_cert_arn_param_name="passian-fbm-vpn-server-cert-arn"
            ),
            NodeConfig(
                name_prefix="FbmNodeB",
                stack_name="FbmNodeStackB",
                site_name="Clinical Node B",
                domain_name="passian.clinicalb",
                bucket_name="clinical-node-b-import-bucket",
                enable_training_plan_approval=True,
                allow_default_training_plans=False,
                use_production_gui=False,
                vpn_cert_arn_param_name="passian-fbm-vpn-server-cert-arn"
            )
        ]
    )
    assert config == expected


def test_parse_config():
    config = configparser.ConfigParser()
    config['network'] = {
        'name_prefix': 'my-prefix',
        'site_name': 'my-site-name',
        'domain_name': 'my-domain-name',
        'vpn_cert_arn_param_name': "network-cert"
    }
    config['node-a'] = {
        'name_prefix': 'my-node-prefix',
        'site_name': 'my-node-site-name',
        'domain_name': 'my-node-domain-name',
        'stack_name': 'my-node-stack-name',
        'bucket_name': 'my-bucket-name',
        'enable_training_plan_approval': 'True',
        'allow_default_training_plans': 'true',
        'use_production_gui': 'False',
        'vpn_cert_arn_param_name': "node-cert"
    }
    config['node-b'] = {
        'name_prefix': 'my-nodeb-prefix',
        'site_name': 'my-nodeb-site-name',
        'domain_name': 'my-nodeb-domain-name',
        'stack_name': 'my-nodeb-stack-name',
        'bucket_name': 'my-bucketb-name',
        'enable_training_plan_approval': 'False',
        'allow_default_training_plans': 'yes',
        'use_production_gui': 'TRUE',
        'vpn_cert_arn_param_name': "nodeb-cert"
    }
    expected = Config(
        network=NetworkConfig(
            name_prefix="my-prefix",
            site_name="my-site-name",
            domain_name="my-domain-name",
            vpn_cert_arn_param_name="network-cert"
        ),
        nodes=[
            NodeConfig(
                name_prefix="my-node-prefix",
                stack_name="my-node-stack-name",
                site_name="my-node-site-name",
                domain_name="my-node-domain-name",
                bucket_name="my-bucket-name",
                enable_training_plan_approval=True,
                allow_default_training_plans=True,
                use_production_gui=False,
                vpn_cert_arn_param_name="node-cert"
            ),
            NodeConfig(
                name_prefix="my-nodeb-prefix",
                stack_name="my-nodeb-stack-name",
                site_name="my-nodeb-site-name",
                domain_name="my-nodeb-domain-name",
                bucket_name="my-bucketb-name",
                enable_training_plan_approval=False,
                allow_default_training_plans=True,
                use_production_gui=True,
                vpn_cert_arn_param_name="nodeb-cert"
            ),
        ]
    )
    assert parse_config(config) == expected


@dataclass
class DataTest:
    stringtype: str
    true1: bool
    true2: bool
    true3: bool
    true4: bool
    true5: bool
    false1: bool
    false2: bool
    false3: bool
    false4: bool
    false5: bool


def test_convert_to():
    config = configparser.ConfigParser()
    config['test'] = {
        'stringtype': 'my-string',
        'true1': 'True',
        'true2': 'true',
        'true3': 'TRUE',
        'true4': 'YES',
        'true5': '1',
        'false1': 'False',
        'false2': 'false',
        'false3': 'FALSE',
        'false4': 'NO',
        'false5': '0'
    }
    assert convert_to(config['test'], key="stringtype", field_type=str) == 'my-string'
    assert convert_to(config['test'], key="true1", field_type=bool)
    assert convert_to(config['test'], key="true2", field_type=bool)
    assert convert_to(config['test'], key="true3", field_type=bool)
    assert convert_to(config['test'], key="true4", field_type=bool)
    assert convert_to(config['test'], key="true5", field_type=bool)
    assert not convert_to(config['test'], key="false1", field_type=bool)
    assert not convert_to(config['test'], key="false2", field_type=bool)
    assert not convert_to(config['test'], key="false3", field_type=bool)
    assert not convert_to(config['test'], key="false4", field_type=bool)
    assert not convert_to(config['test'], key="false5", field_type=bool)


def test_convert_inputs():
    config = configparser.ConfigParser()
    config['test'] = {
        'stringtype': 'my-string',
        'true1': 'True',
        'true2': 'true',
        'true3': 'TRUE',
        'true4': 'YES',
        'true5': '1',
        'false1': 'False',
        'false2': 'false',
        'false3': 'FALSE',
        'false4': 'NO',
        'false5': '0'
    }
    assert convert_inputs(dataclass_type=DataTest, section=config['test']) == \
        DataTest(
            stringtype='my-string',
            true1=True,
            true2=True,
            true3=True,
            true4=True,
            true5=True,
            false1=False,
            false2=False,
            false3=False,
            false4=False,
            false5=False
        )
