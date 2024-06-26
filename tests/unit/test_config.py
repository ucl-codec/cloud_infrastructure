import configparser
from dataclasses import dataclass

from aws_fbm.utils.config import read_config_file, Config, NetworkConfig, \
    NodeConfig, parse_config, convert_inputs, convert_to


def test_dev_config():
    """Test development stack configuration is correctly parsed"""
    config = read_config_file("dev")
    expected = Config(
        network=NetworkConfig(
            config_name="dev",
            node_name="network",
            stack_name=None,
            name_prefix="passianfl-dev-network-",
            site_description="Development researcher node",
            domain_name="researcher.passianfldev.com",
            use_https=False
        ),
        nodes=[
            NodeConfig(
                config_name="dev",
                node_name="nodea",
                name_prefix='passianfl-dev-nodea-',
                stack_name=None,
                site_description="Development node a",
                domain_name="nodea.passianfldev.com",
                enable_training_plan_approval=False,
                allow_default_training_plans=True,
                use_production_gui=True,
                default_gui_username="admin@testclinicala",
                use_https=False
            )
        ]
    )
    assert config == expected
    assert config.nodes[0].import_bucket_name == "passianfl-dev-nodea-import-bucket"


def test_prod_config():
    """Test production stack configuration is correctly parsed"""
    config = read_config_file("prod")
    expected = Config(
        network=NetworkConfig(
            config_name="prod",
            node_name="network",
            name_prefix="Fbm",
            stack_name="FbmNetworkStack",
            site_description="Federated",
            domain_name="passian.federated"
        ),
        nodes=[
            NodeConfig(
                config_name="prod",
                node_name="nodea",
                name_prefix="FbmNodeA",
                stack_name="FbmNodeStackA",
                site_description="Clinical Node A",
                domain_name="passian.clinicala",
                enable_training_plan_approval=False,
                allow_default_training_plans=False,
                use_production_gui=False,
                default_gui_username="admin@clinicala",
            ),
            NodeConfig(
                config_name="prod",
                node_name="nodeb",
                name_prefix="FbmNodeB",
                stack_name="FbmNodeStackB",
                site_description="Clinical Node B",
                domain_name="passian.clinicalb",
                enable_training_plan_approval=False,
                allow_default_training_plans=False,
                use_production_gui=False,
                default_gui_username="admin@clinicalb",
            )
        ]
    )
    assert config == expected
    assert config.nodes[0].import_bucket_name == "passianfl-prod-nodea-import-bucket"
    assert config.nodes[1].import_bucket_name == "passianfl-prod-nodeb-import-bucket"


def test_parse_config():
    """Test the parse_config function"""

    config = configparser.ConfigParser()
    config['network'] = {
        'name_prefix': 'my-prefix',
        'site_description': 'my-site-name',
        'domain_name': 'my-domain-name'
    }
    config['node-a'] = {
        'name_prefix': 'my-node-prefix',
        'site_description': 'my-node-site-name',
        'domain_name': 'my-node-domain-name',
        'stack_name': 'my-node-stack-name',
        'enable_training_plan_approval': 'True',
        'allow_default_training_plans': 'False',
        'use_production_gui': 'False',
        'default_gui_username': 'admin.node'
    }
    config['node-b'] = {
        'name_prefix': 'my-nodeb-prefix',
        'site_description': 'my-nodeb-site-name',
        'domain_name': 'my-nodeb-domain-name',
        'stack_name': 'my-nodeb-stack-name',
        'enable_training_plan_approval': 'False',
        'allow_default_training_plans': 'True',
        'use_production_gui': 'TRUE',
        'default_gui_username': 'admin.nodeb'
    }
    expected = Config(
        network=NetworkConfig(
            config_name="my-config",
            node_name="network",
            name_prefix="my-prefix",
            site_description="my-site-name",
            domain_name="my-domain-name"
        ),
        nodes=[
            NodeConfig(
                config_name="my-config",
                node_name="node-a",
                name_prefix="my-node-prefix",
                stack_name="my-node-stack-name",
                site_description="my-node-site-name",
                domain_name="my-node-domain-name",
                enable_training_plan_approval=True,
                allow_default_training_plans=False,
                use_production_gui=False,
                default_gui_username="admin.node",
            ),
            NodeConfig(
                config_name="my-config",
                node_name="node-b",
                name_prefix="my-nodeb-prefix",
                stack_name="my-nodeb-stack-name",
                site_description="my-nodeb-site-name",
                domain_name="my-nodeb-domain-name",
                enable_training_plan_approval=False,
                allow_default_training_plans=True,
                use_production_gui=True,
                default_gui_username="admin.nodeb",
            )
        ]
    )
    assert parse_config(config_name="my-config", config=config) == expected
    assert expected.nodes[0].import_bucket_name == "passianfl-my-config-node-a-import-bucket"


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
    """Test the convert_to function"""

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
    """Test the convert_inputs function"""

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
    assert convert_inputs(
        dataclass_type=DataTest,
        section=config['test']) == \
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
