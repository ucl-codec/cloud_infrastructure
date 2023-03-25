# Installing PassianFL

PassianFL is deployed in AWS using the Python AWS CDK. Deployment and update can be initiated 
from your local machine using the following instructions.

---
## Requirements

### AWS account

 - An AWS account
 - Sufficient funds to host a PassianFL installation 
 - An AWS IAM user account with sufficient permissions to perform the installation

### The machine you will use to perform the deployment

 - git client
 - permissions to clone this repository and its Fed-BioMed fork
 - AWS CLI
 - Python 3 and venv (recommended)
 - AWS python CDK packages (aws-cdk-lib, constructs) - listed in requirements.txt
 - Other python dependencies - see requirements.txt
 - A version of node supported by AWS (preferably installed using nvm)
 - Docker, including the docker CLI and a docker engine (such as Docker Desktop)
   - Sufficient disk space available to the docker VM to build the docker images (recommended 100GB+) 
   - Sufficient RAM available to the docker VM to build the docker images (recommended 8GB+) 

See below for detailed installation instructions.



---

## Set up your local machine for AWS deployment

Please follow the instructions in [Setting up a local machine to deploy Passian FL on AWS](deployment-machine-setup.md)

---

## Configuring your AWS credentials

Please follow the instructions in [Configure your AWS credentials](configure-aws-credentials.md)


---

## PassianFL configuration files

Before deployment, you must create your own PassianFL configuration file, or use one of the
existing templates provided. Please follow the instructions in [Configuration files](configuration-files.md)


---

## Configure a custom domain to enable https encryption

If you wish to enable https encryption to the web servers (recommended), you must own or have 
control of a public web domain. This is in order to allow AWS to generate and verify 
certificates that will be recognised by your web browser.

- Please follow the instructions in [Enabling https](enabling-https.md) before deploying a system with
https enabled

---

## One-time setup

These actions must be performed once before installing PassianFL for the first time

### CDK bootstrap

If this CDK stack has not previously been deployed on this AWS account, you can run a bootstrap to
set up the resources necessary for CDK to run.
```bash
cdk bootstrap --profile passian
```

### Create VPN certificate authority and server certificates

The VPN server certificates must exist before you can run the CDK deployment.

For a development environment, the script `/scripts/initialise.sh` will automatically create these 
for you based on your configuration file, using the `easyrsa` utility.
The keys and certificates will be created in your home directory under `~/passian_vpn_certificates`. 
For this reason, you should only run this on a machine
where you can keep this folder secure. You will need to generate client certificates on the same 
machine, or else securely move the certificate authority files across.

Ensure you have set up your configuration file before running this command. See [Configuration files](configuration-files.md)

From the repository directory, run the initialisation script
```bash
./scripts/initialise.sh <config-name> <aws-profile-name>
```
  - Replace `<config-name>` with the name of your configuration file in the config directory (excluding `.cfg`), e.g. `dev`
  - Replace `<aws-profile-name>` with the name of your aws profile, e.g. `passian`

For example, to initialise the `dev` configuration:
```bash
scripts/initialise.sh dev passian
```

If initialisation fails (for example if you have not installed all the required dependencies), you may need to manually create the
required resources

The resources this script creates are:
- For the Researcher Node and each Local Node, a development CA and server certificate for accessing the VPN 


---
## VPN with production deployments

The `initialise.sh` and `create_vpn_client.sh` scripts provide a convenient way of quickly creating and distributing
VPN credentials for a development system. The certificate authority files and keys are stored in your home directory,
and client configuration files are distributed as SecureStrings via the AWS Parameter Store. This 
will not in general be appropriate for a production system, where it is necessary to strictly maintain the secrecy of keys and credentials

For production deployments, ensure keys are only stored on a secure system. You may wish to consider 
your own secure mechanisms for creating and distributing keys and certificates, or using an alternative method for
VPN authorisation. Please see the [AWS VPN documentation](https://docs.aws.amazon.com/vpn/latest/clientvpn-admin/client-authentication.html)  .

---

## CDK deployment and update  

You can synthesize the CloudFormation template prior to deployment. This is not essential as it 
will be performed automatically when you deploy, but it is a useful check as it helps to identify errors.

When invoking the cdk commands, use `--context config=<config-name>` to specify your configuration file name.
For example, to synthesise the dev configuration, use

```bash
cdk synth --context config=dev --profile passian
```

To deploy the dev stack
```bash
cdk deploy --all  --context config=dev --profile passian
```

There are helper scripts to depoloy dev and production: 

- Deploy dev:
    ```bash
    ./scripts/deploy_dev.sh
    ```
- Deploy production:
    ```bash
    ./scripts/deploy_prod.sh
    ```

---

## Change the Fed-BioMed gui admin password

After the local nodes have been deployed, you should log into the Fed-BioMed gui on each node and
change the admin password. You may also wish to create Fed-BioMed user accounts for the data 
providers 

- You will need to generate a VPN client configuration file for yourself for each node you wish to 
connect to. See [Adding users](adding-users.md)
- You then need to set up VPN access for each node by adding this file to the AWS Client VPN. See
[VPN setup](../user_guide/vpn_setup.md)
- Once connected to the local node VPN, you can connect to the Fed-BioMed gui as described in the [user guide](../user_guide/user_guide.md).
- The default credentials for the Fed-BioMed admin user are as follows:
  - The admin username is specified in the configuration file, e.g. `conf/prod.cfg` 
  - The default admin password is stored in an AWS secret with the prefix `passianfl<config-name><node-name>guidefault-xxxxxx`
  where `<config-name>` is the name of the configuration file and `<node-name>` the name of the node
  (this is the name of that node's section in the configuration file). 


---
## Destroy the CDK stack

To remove a deployment, you can either:
- run cdk destroy from your machine to destroy the CDK stacks
- delete the CloudFormation stacks on the AWS Console

Do not delete resources manually, as you may then be unable to perform further CDK updates.

You should only manually delete resources in one of following situations:
 - they were created outside of CDK (such as by the `initialise.sh` script above)
 - where the stack has already been destroyed and a resource remains because it could not be deleted

Some stacks are protected from deletion, as they contain "stateful" resources (such as the file systems and VPN).
Destroying these could result in data loss or users having to obtain new VPN credentials.
To remove protected stacks, you will first need to disable stack protection using the AWS console. 

A convenience script is provided for destroying the production stack:
```bash
./scripts/destroy.sh
```
Note that some resources are defined outside of the CDK stacks and will persist (such as parameters, certificates and S3 buckets).
These need to be manually deleted to stop further costs.

---
## Troubleshooting

See [Troubleshooting](troubleshooting.md)

