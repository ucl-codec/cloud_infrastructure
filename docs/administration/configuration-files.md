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
param_vpn_cert_arn = passianfl-node-a-vpn-server-cert-arn
default_gui_username = admin@passianfl.localnodea
param_default_gui_pw = passianfl-node-a-default-gui-pw

[node-b]
name_prefix = LocalNodeB
site_description =  Local Node N
domain_name = passianfl.localnodeb
bucket_name = local-node-b-import-bucket
param_vpn_cert_arn = passianfl-node-b-vpn-server-cert-arn
default_gui_username = admin@passianfl.localnodeb
param_default_gui_pw = passianfl-node-b-default-gui-pw
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
- `default_gui_username`: The Fed-BioMed gui default admin username. Only used when the system is first run to set up an initial admin user
- `param_default_gui_pw`: The name of a SecureString AWS parameter which holds the initial password for the Fed-BioMed gui admin user.
The `initialise.sh` script will populate it for you if it does not already exist. This is only used the first time
the gui is run. 
