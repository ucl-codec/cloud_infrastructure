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

    network_config = NetworkConfig(
        name_prefix=config[network_section]['name_prefix'],
        site_name=config[network_section]['site_name'],
        domain_name=config[network_section]['domain_name']
    )

    nodes = []
    for section in config.sections():
        if section != network_section:
            nodes.append(NodeConfig(
                name_prefix=config[section]['name_prefix'],
                stack_name=config[section]['stack_name'],
                site_name=config[section]['site_name'],
                domain_name=config[section]['domain_name'],
                bucket_name=config[section]['bucket_name']
            ))
    return Config(network=network_config, nodes=nodes)
