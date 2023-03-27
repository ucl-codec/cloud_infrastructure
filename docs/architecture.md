# Architecture

---

## Stack architecture

There is one VPC for the Researcher Node and one for each of the Local Nodes.

These are divided into multiple stacks:

Researcher Node:
- NetworkStack: stateful resources (VPC, VPN, storage)
- NetworkServicesStack: cluster of FBM federation services (mqtt + restful)
- ResearcherServicesStack: cluster of researcher services (jupyter + tensorboard)

Each Local Node:
- DataImportStack: S3 import bucket
- NodeStack: other stateful resources (VPC, VPN, storage)
- NodeServicesStack: cluster of node services (FBM node + FBM gui)

Peering Stack: connects the VPCs together

