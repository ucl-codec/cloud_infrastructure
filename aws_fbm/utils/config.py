from typing import List, Type, Optional

from aws_fbm.utils.utils import repo_path
from dataclasses import dataclass, fields

from configparser import ConfigParser, SectionProxy, RawConfigParser
import os


@dataclass
class NetworkConfig:
    """Configuration for a Federated network

    The configuration is stored in a config file e.g. config/dev.cfg
    which is automatically parsed to create an object of this class
    """

    node_name: str  # Always "network"
    name_prefix: str  # used to generate stack names - must be unique
    site_description: str  # human-readable name of the Researcher site
    domain_name: str  # domain used when connected to the Researcher VPN
    param_vpn_cert_arn: str  # AWS parameter storing the vpn cert arn


@dataclass
class NodeConfig:
    """Configuration for a Data Node

    The configuration is stored in a config file e.g. config/dev.cfg
    which is automatically parsed to create an object of this class
    """

    node_name: str  # Name of node, from the section name in the config file
    name_prefix: str  # used to generate stack names - must be unique
    site_description: str  # human-readable name of the Data Node site
    domain_name: str  # domain used when connected to the Data Node VPN
    bucket_name: str  # Persistent data bucket for this Data Node
    param_vpn_cert_arn: str  # AWS parameter storing the vpn cert arn
    default_gui_username: str  # FBM default gui admin username
    param_default_gui_pw: str  # AWS parameter storing default FBM gui password
    enable_training_plan_approval: bool = True  # FBM training must be approved
    allow_default_training_plans: bool = False  # FBM permits default training
    use_production_gui: bool = True  # True if FBM GUI should use gunicorn
    stack_name: Optional[str] = None  # If specified, overrides the stack name


@dataclass
class Config:
    """Configuration for a PassianFL system

    The configuration is stored in a config file e.g. config/dev.cfg
    which is automatically parsed to create an object of this class
    """
    network: NetworkConfig  # Configuration for the Federated network
    nodes: List[NodeConfig]  # Configuration for Data Nodes


def read_config_file(config_name: str) -> Config:
    """Read config file from config folder and parse to Config class"""
    if not config_name:
        raise RuntimeError("A config (prod or dev) must be specified, e.g. "
                           "cdk --context config=dev")
    config_filename = repo_path() / "config" / config_name
    config_filename = config_filename.with_suffix(".cfg")
    if not os.path.isfile(config_filename):
        raise RuntimeError(f"Unknown config {config_filename} was specified")

    config = RawConfigParser()
    config.read(config_filename)
    return parse_config(config=config)


def parse_config(config: ConfigParser):
    """Convert returned config structure to Config object"""
    network_section = "network"
    return Config(
        network=convert_inputs(
            dataclass_type=NetworkConfig,
            section=config[network_section],
            node_name="network"),
        nodes=[convert_inputs(
            dataclass_type=NodeConfig,
            section=config[section],
            node_name=section) for
               section in config.sections() if section != network_section]
    )


def convert_inputs(dataclass_type: Type, section: SectionProxy, **kwargs):
    """Convert this config section into a dataclas object, converting the string
    variables where necessary"""
    field_types = {field.name: field.type for field in fields(dataclass_type)}
    converted = {
        key: convert_to(section=section,
                        key=key,
                        field_type=field_types[key]) for key in section
    }
    return dataclass_type(**converted, **kwargs)


def convert_to(section: SectionProxy, key: str, field_type: Type):
    """Fetch the given key from the config section, converting to the specified
    type if required"""
    return section.getboolean(key) if field_type == bool else section.get(key)
