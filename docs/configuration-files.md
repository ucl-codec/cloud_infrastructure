# PassianFL configuration files

A PassianFL system is described by a configuration stored in the `config` folder, for example:
- `config/prod.cfg` describes a "production" system with one Researcher and two Local Nodes 
- `config/dev.cfg` describes a "development" system with one Researcher and one Local Nodes 

You can use or modify the existing files, or create your own file.

You must create the file before deploying your PassianFL system, as you will need it to generate
the resources that are required prior to CDK deployment.

---

## Description of configuration file

Example configuration file:
```
[network]
name_prefix = Passian
site_description =  PassianFL
domain_name = passianfl.researcher
param_vpn_cert_arn = passianfl-network-vpn-server-cert-arn

[node-a]
name_prefix = LocalNodeA
stack_name = LocalNodeAStack
site_description =  Local Node A
domain_name = passianfl.localnodea
bucket_name = local-node-a-import-bucket
default_gui_username = admin@passianfl.localnodea

[node-b]
name_prefix = LocalNodeB
site_description =  Local Node N
domain_name = passianfl.localnodeb
bucket_name = local-node-b-import-bucket
default_gui_username = admin@passianfl.localnodeb
```

The `[network]` dession describes the Researcher Node.
Each additional seciton desribes a Local Node.

## Network

- `name_prefix`: Prefix used to name the CloudFormation stacks. Must be unique in your account
- `site_description`: Human readable name for the Researcher Node; only used in descriptions
- `domain_name`: The private hosted zone domain name that researchers will use to access resources 
while connected to the VPN. For example, if `domain_name` is `passianfl.researcher`, then 
researchers will access jupyter at `http://jupyter.passianfl.researcher`

## Local Nodes
- `name_prefix`: Prefix used to name the CloudFormation stacks. Must be unique in your account
- `stack_name`: (optional) overrides the Cloud Formation stack name. Not required in general
- `site_description`: Human readable name for the Local Node; only used in descriptions
- `domain_name`: The private hosted zone domain name that Local Node data providesr will use to access resources 
while connected to the VPN. For example, if `domain_name` is `passianfl.nodea`, then 
researchers will access the FBM gui at `http://gui.passianfl.nodea`
- `bucket_name`: The name of the S3 bucket used to import data into this Local Node. This must be unique.
for each node. The `initialise.sh` script will create the bucket if it does not exist.
- `default_gui_username`: The Fed-BioMed gui default admin username. Only used when the system is 
first run to set up an initial admin user. The default password is created during the AWS deployment
and stored as an AWS secret with the name `passianfl<config-name><node-name>guidefault-xxxxxx`
where `<config-name>` is the name of the configuration file and `<node-name>` the name of the node
which is the name of that node's section in the configuration file.  
