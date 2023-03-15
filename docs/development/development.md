# Development and installation guide for Passian Learning

This is a Python CDK project for building Passian Learning on AWS

---

## Setting up your system for AWS deployment

### Clone this repository and initialise submodules
   ```bash
   git clone <this-repo-url> <your-path>
   git submodule init
   git submodule update
   ```
### Install the AWS CLI
- Follow the AWS docs: https://docs.aws.amazon.com/cli/latest/userguide/getting-started-install.html

### Create an AWS Access Key
- You can do this on the AWS Console: https://docs.aws.amazon.com/IAM/latest/UserGuide/id_credentials_access-keys.html

### Create an AWS named profile on your machine, named `passian`
```bash
aws configure --profile passian 
```
This will create entries in `~/.aws/credentials` and `~/.aws/config`. Alternately, you can set 
these up manually. For more details, see https://docs.aws.amazon.com/cli/latest/userguide/cli-configure-profiles.html

### Create a python virtual environment
 
This is so that you can install the aws CDK libraries without affecting your system python installation 
Ensure you have a recent version of python 3 installed (but do not modify your system python installation)
Install venv if you do not have it installed

Create a new virtual environment using
```
python3 -m venv .aws_fbm_env
```

Activate the environment. You will need to do this when returning in the future.
```bash
source .aws_fbm_env/bin/activate
```

After creating and activating the environment, install the dependencies within this environment
```bash
pip install -r requirements.txt
```
   
### Install the AWS CDK
```bash
python -m pip install aws-cdk-lib
```

### Install Docker
- CDK will build the Docker images locally as part of deployment, so you need both the Docker SDK installed, and also a Docker VM (such as Docker Desktop or Rancher Desktop)
- Docker Desktop and Rancher Desktop run Docker inside a VM; you may want to increase the RAM available to the VM to speed up builds.

### Install nvm and node
It strongly recommended that you use nvm to install/manage node and do not install node directly.
- Install nvm
- Use nvm to install latest LTS version of node
   ```bash
    nvm install --lts
   ```

### Install the AWS CDK

```bash
npm install -g aws-cdk
```

## Local docker testing 

You can build and run the docker containers on your local machine using the helper scripts.
This will give you a fully working test Passian Learning instance on your local machine.

### Build the docker files on your local machine
```bash
./local_development/local_docker_build.sh
```

### Run the docker files on your local machine
```bash
./local_development/local_docker_run.sh
```

If the build and run succeed, you should be able to access the containers via localhost:
  - Fed-BioMed Node gui: http://localhost:8484
  - Jupyter notebook: http://localhost:8888
  - TensorBoard: http://localhost:6007

### SSH into the docker containers while they are running
```bash
docker exec -it node bash
docker exec -it researcher bash
docker exec -it gui bash
docker exec -it mqtt bash
docker exec -it restful bash
```

### Destroy the containers
```bash
./local_development/local_docker_destroy.sh
```

### Persistent files

Persistent files (data etc.) for the Docker deployment are stored in `.local_docker_storage`. You 
may wish to delete this folder after destroying the containers in order to reclaim disk space.

## Docker troubleshooting

See Troubleshooting below.

---

## AWS setup  

### One-time setup

If this CDK stack has not previously been deployed on this AWS account, you can run a bootstrap to
set up the resources necessary for CDK to run.
```bash
cdk bootstrap --profile passian
```

### VPN server 

#### Create VPN server certificate
You need to generate a development CA for the VPN and add the key, certificate and CA chain to the
AWS Certificate Manager. You will need to reference the ARN of this certificate in the CDK
codebase. You will need to use this CA to generate development VPN certificates.

For more details: https://docs.aws.amazon.com/vpn/latest/clientvpn-admin/client-authentication.html#mutual

#### Add ARN of VPN server certificate to parameter store

Once you have added this certificate to the AWS Certificate Manager, you need to create a parameter
which the CDK templates will use to identify the certificate.

To do this, create a parameter in the AWS Parameter Store called `passian-fbm-vpn-server-cert-arn`.
This should be a String, and the value should be the ARN (Amazon Resource Name) of the cerficiate. 

---

## AWS deployment  

You can synthesize the CloudFormation template prior to deployment. This is not essential as it 
will be performed automatically when you deploy, but it is a useful check .

```bash
cdk synth --profile passian
```

Deploy the stack
```bash
./scripts/deploy.sh
```

### Destroy the AWS stack
```bash
./scripts/destroy.sh
```
Note that some resources may persist (such as volumes). These need to be manually deleted on the
AWS console to stop further costs.


## Troubleshooting

### Docker errors

- Can't connect to docker daemon. Is 'docker -d' running on this host?

This is likely because you haven't installed a Docker engine, or it is not currently running.

On macOS/Windows, you can install a Docker engine by installing Docker Desktop or compatible 
alternatives such as Rancher Desktop or Colima. Note this in addition to installing the Docker command line.
The Engine provides a linux VM where Docker actually runs the builds

If your docker engine is not set to launch automatically, you can launch it by running the Docker 
Desktop or Rancher Desktop gui, or using the appropriate command-line calls.  

### Errors during Docker container building

Common intermittent build errors are due to the Docker engine having insufficient RAM or disk space.
You can adjust the RAM and disk space in the engine'e settings.
 - In Docker Desktop, launch the GUI and go to Settings/Resources.

### No space left on device

This refers to the disk space available to the Docker engine. You can increase this through the
engine's settings as described above.

In addition, old images and volumes may fill up your engine's disk space. To reclaim space, use docker prune 
commands. Note however that pruning may increase build time or force a complete rebuild 

Example commands (see docker documentation for more details)
- Remove unused images: `docker system prune`
- Remove all images: `docker system prune --all --force`
- Remove all docker volumes: `docker system prune --all --force --volumes`

### exit code: 13

`exit code: 13` during a local docker build indicates you need to increase the maximum RAM 
available to the local docker VM. You can adjust the RAM and disk space in the engine'e settings 
as described above



---
