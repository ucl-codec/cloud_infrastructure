from typing import List, Type

from aws_fbm.utils.utils import repo_path
from dataclasses import dataclass, fields

from configparser import ConfigParser, SectionProxy, RawConfigParser
import os


@dataclass
class NodeConfig:
    stack_name: str
    name_prefix: str
    site_name: str
    domain_name: str
    bucket_name: str
    enable_training_plan_approval: bool = True
    allow_default_training_plans: bool = False
    use_production_gui: bool = True


@dataclass
class NetworkConfig:
    name_prefix: str
    site_name: str
    domain_name: str


@dataclass
class Config:
    network: NetworkConfig
    nodes: List[NodeConfig]


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
    return parse_config(config)


def parse_config(config: ConfigParser):
    """Convert returned config structure to Config object"""
    network_section = "network"
    return Config(
        network=convert_inputs(
            dataclass_type=NetworkConfig, section=config[network_section]),
        nodes=[convert_inputs(
            dataclass_type=NodeConfig, section=config[section]) for
               section in config.sections() if section != network_section]
    )


def convert_inputs(dataclass_type: Type, section: SectionProxy):
    """Convert this config section into a dataclas object, converting the string
    variables where necessary"""
    field_types = {field.name: field.type for field in fields(dataclass_type)}
    converted = {
        key: convert_to(section=section,
                        key=key,
                        field_type=field_types[key]) for key in section
    }
    return dataclass_type(**converted)


def convert_to(section: SectionProxy, key: str, field_type: Type):
    """Fetch the given key from the config section, converting to the specified
    type if required"""
    return section.getboolean(key) if field_type == bool else section.get(key)
