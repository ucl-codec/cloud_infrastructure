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

---

## Architecture diagram

![Diagram showing PassianFL AWS architecture](passianfl_architecture.png)

---

## Component summary

- Services:
  - Services are docker containers deployed using ECS. The containers are stored in ECR
  - The node service is an EC2 service with ASG/capacity provider providing GPU-enabled EC2 instances
  - The mqtt, restful, gui, jupyter, tensorboard services are Fargate services
  - The web services (gui, restful, jupyter, tensorboard) are fronted by Application Load Balancers
  - The mqtt service is fronted by a Network Load Balancer
- Storage
  - The researcher node and each local node has its own persistent EFS
  - Each local node has an S3 data import bucket, which is automatically synced to the local node EFS using AWS DataSync 
- Networking
  - The researcher node and each local node has its own VPC
  - Each VPC has two private subnets from two AZs
  - The researcher node and each local node has its own VPN
  - VPC peering allows connections to the mqtt and restful services from the local nodes
  - No external internet access is enabled within the VPCs. Access to AWS services is through interface endpoints (AWS PrivateLink)
