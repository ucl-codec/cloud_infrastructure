# Setting up a local machine to deploy Passian FL on AWS

---

## Clone this repository
```bash
git clone <this-repo-url> <your-path>
```

### Initialise submodules

Note that a custom Fed-BioMed fork is included as a submodule (in `docker/common`).

You *must* initialise the submodule and update when required for the deployment to work  
 ```bash
 cd cloud_infrastructure
 git submodule init
 git submodule update
 ```

---

## Install the AWS CLI

Follow the AWS docs: https://docs.aws.amazon.com/cli/latest/userguide/getting-started-install.html

---

## Install python and dependencies

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

---
## Install Docker
CDK will build the Docker images locally as part of deployment, so you need both the Docker SDK installed, and also a Docker VM (such as Docker Desktop or Rancher Desktop)

### Increase the memory and disk limit for your Docker VM
- Docker Desktop and Rancher Desktop run Docker inside a VM; you may need to increase the RAM and disk space available to the VM in order to successfully build the images and to speed up the builds.
- In Docker Desktop you can adjust the memory and Virtual disk limit in `Settings` > `Resources` > `Advanced`
  - Recommended: >8GB RAM, >100GB disk limit

---

## Install nvm and node
It strongly recommended that you use nvm to install/manage node and do not install node directly.
- Install nvm
  - macOS note: you can install nvm through homebrew. Install homebrew if necessary and then run `brew install nvm`. Make sure you follow the additional instructions - you need to modify your .zshrc file if you are using zsh shell which is default on new macs. If you are using bash, modify .bash_profile instead. You then need to open a new terminal window, or source .zshrc or .bash_profile before continuing in the current window.
- Use nvm to install latest LTS version of node
   ```bash
    nvm install --lts
   ```

---
### Install the AWS CDK

```bash
npm install -g aws-cdk
```

---

### Create an AWS Access Key
- You can do this on the AWS Console: https://docs.aws.amazon.com/IAM/latest/UserGuide/id_credentials_access-keys.html

### Create an AWS named profile on your machine, named `passian`
```bash
aws configure --profile passian 
```
This will create entries in `~/.aws/credentials` and `~/.aws/config`. Alternately, you can set 
these up manually. For more details, see https://docs.aws.amazon.com/cli/latest/userguide/cli-configure-profiles.html


