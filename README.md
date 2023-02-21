# AWS stack for PASSIAN with Fed-BioMed

This is a Python CDK project for building Fed-BioMed on AWS

---
## Connecting to a running AWS deployment of Fed-BioMed

If a development stack is already running, you can connect to the Researcher or Clinical nodes
using VPN and your web browser


### Install the AWS Client VPN
https://aws.amazon.com/vpn/client-vpn-download/

### Obtain your development VPN certificates

- Development certificates are stored as secure strings in the AWS Parameter Store. 
- You require separate certificates for the researcher VPN and the clinical VPN

### Add the certificates to the AWS VPN Client
- Launch AWS VPN Client 
- Go to Manage Profiles
- Add the two certificate files with profile names `Researcher` and `Clinical`

### Connect to the Researcher network
- Launch AWS VPN Client 
- Select Researcher profile
- Click Connect
- Connect to Jupyter notebook in your web browser: http://researcher.passian:8888
- Connect to TensorBoard in your web browser: http://researcher.passian:6007

### Connect to the Clinical network

- Launch AWS VPN Client 
- Select Clinical profile
- Click Connect
- Connect to Fed Bio-Med GUI in your web browser: http://node.passian:8484

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

Whenever you need to reactivate the environment in future, you do this with 
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

### Install nvm and node
It strongly recommended that you use nvm to install/manage node and do not install node directly.
- Install nvm
- Use nvm to install latest LTS version of node
   ```bash
    nvm install --lts
   ```


---

## Local docker testing 

You can build and run the docker containers on your local machine using the helper scripts.
This will give you a fully working test Fed-BioMed instance on your local machine.

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

`exit code: 13` during a local docker build indicates you need to increase the maximum RAM 
available to the local docker VM. This is not a build argument but is configured in the Docker VM
provider preferences (e.g. Docker Desktop, Rancher Desktop)

---

## AWS setup  

### One-time setup

If this CDK stack has not previously been deployed on this AWS account, you can run a bootstrap to
set up the resources necessary for CDK to run.
```bash
cdk bootstrap
```

### VPN server 

You need to generate a development CA for the VPN and add the key, certificate and CA chain to the
AWS Certificate Manager. You will need to reference the ARN of this certificate in the CDK
codebase. You will need to use this CA to generate development VPN certificates.

For more details: https://docs.aws.amazon.com/vpn/latest/clientvpn-admin/client-authentication.html#mutual

---

## AWS deployment  

### Deployment

You can synthesize the CloudFormation template prior to deployment. This is not essential as it 
will be performed automatically when you deploy, but it is a useful check  

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

`exit code: 13` during a local docker build indicates you need to increase the maximum RAM 
available to the local docker VM. This is not a build argument but is configured in the Docker VM
provider (e.g. Docker Desktop or Rancher Desktop)

---
