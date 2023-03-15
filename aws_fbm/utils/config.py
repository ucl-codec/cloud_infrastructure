from typing import List

from aws_fbm.utils.utils import repo_path
from dataclasses import dataclass

import configparser
import os


@dataclass
class NodeConfig:
    stack_name: str
    name_prefix: str
    site_name: str
    domain_name: str
    bucket_name: str


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
    if not config_name:
        raise RuntimeError("A config (prod or dev) must be specified, e.g. "
                           "cdk --context config=dev")
    config_filename = repo_path() / "config" / config_name
    config_filename = config_filename.with_suffix(".cfg")
    if not os.path.isfile(config_filename):
        raise RuntimeError(f"Unknown config {config_filename} was specified")

    config = configparser.RawConfigParser()
    config.read(config_filename)
    network_section = "network"

    network_config = NetworkConfig(**config[network_section])

    nodes = []
    for section in config.sections():
        if section != network_section:
            nodes.append(NodeConfig(**config[section]))
    return Config(network=network_config, nodes=nodes)
