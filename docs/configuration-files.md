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
site_description = PassianFL researcher node
domain_name = researcher.passianfl.com
use_https = True

[nodea]
site_description =  PassianFL local node A
domain_name = nodea.passianfl.com
default_gui_username = admin@nodea.passianfl.com
use_https = True
enable_training_plan_approval = True
allow_default_training_plans = False


[nodeb]
site_description =  PassianFL local node B
domain_name = nodeb.passianfl.com
default_gui_username = admin@nodeb.passianfl.com
use_https = True
enable_training_plan_approval = True
allow_default_training_plans = False
```

The `[network]` dession describes the Researcher Node.
Each additional seciton desribes a Local Node.

## Network

- `site_description`: Human readable name for the Researcher Node; only used in descriptions
- `domain_name`: The private hosted zone domain name that researchers will use to access resources 
while connected to the VPN. For example, if `domain_name` is `passianfl.researcher`, then 
researchers will access jupyter at `http://jupyter.passianfl.researcher`
- `use_https`: Set to True to use https for the researcher web services. Requires you to have control
of a domain name. See [Enabling https](enabling-https.md)
- `parent_domain`: When `use_https` is set to True, this refers to the parent domain, for which you
have created an AWS Public Hosted Zone. See [Enabling https](enabling-https.md)
- `name_prefix`: (Optional) Prefix used to name the CloudFormation stacks. You do not need to set this
but if you do, it must be unique in your account
- `stack_name`: (Optional) Prefix used to name the main CloudFormation stack. You do not need to set this
but if you do, it must be unique in your account

## Local Nodes
- `site_description`: Human readable name for the Local Node; only used in descriptions
- `domain_name`: The private hosted zone domain name that data providers will use to access resources 
while connected to the VPN. For example, if `domain_name` is `passianfl.nodea`, then 
researchers will access jupyter at `http://gui.passianfl.nodea`
- `default_gui_username`: The Fed-BioMed gui default admin username. Only used when the system is 
first run to set up an initial admin user. The default password is created during the AWS deployment
and stored as an AWS secret with the name `passianfl<config-name><node-name>guidefault-xxxxxx`
where `<config-name>` is the name of the configuration file and `<node-name>` the name of the node
which is the name of that node's section in the configuration file.  
- `use_https`: (Optional) Set to True to use https for the node gui web service. Requires you to have control
of a domain name. See [Enabling https](enabling-https.md)
- `parent_domain`: (Optional) When `use_https` is set to True, this refers to the parent domain, for which you
have created an AWS Public Hosted Zone. See [Enabling https](enabling-https.md)
- `enable_training_plan_approval`: (Optional) Set to True requires the data provider to approve Fed-BioMed training plans
- `allow_default_training_plans`: (Optional) Set to True allows default Fed-BioMed training plans to be automatically approved
- `use_production_gui`: (Optional) Set to True to use a gunicorn web server for the node gui
- `name_prefix`: (Optional) Prefix used to name the CloudFormation stacks. You do not need to set this
but if you do, it must be unique in your account
- `stack_name`: (Optional) Prefix used to name the main CloudFormation stack. You do not need to set this
but if you do, it must be unique in your account
