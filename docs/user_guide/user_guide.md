# User guide for Passian Learning

This guide is for end users of Passian Learning. It assumes you have a fully working installation
of Passian Learning on AWS.

Users may be  
- Researchers: can execute federated training
- Data Providers: can add data to their Data Nodes and approve use of training plans on their data

If you have both of these roles, you need to consider role independently when following the following instructions.

---

## Data Provider 

### Set up your VPN access

- See [Connecting to VPNs for Passian Learning](vpn_setup.md)

### Connect to your Data Node

- Launch the AWS VPN Client 
- Select the VPN profile for your data node:
  - for example `Passian Data Node (your site name)`
- Click `Connect`
- Connect to Fed Bio-Med GUI in your web browser:
  - Site A: http://gui.passian.clinicala
  - Site B: http://gui.passian.clinicalb


### Log into the Fed-BioMed gui
 - The Fed-BioMed gui has its own accounts. Your will need your Passian Learning system administator to 
create an account for you and provide you with the credentials 


---

## Researcher

### Set up your VPN access

- See [Connecting to VPNs for Passian Learning](vpn_setup.md)

### Connect to the Researcher network
- Launch the AWS VPN Client 
- Select your `Passian Researcher` profile
- Click `Connect`
- Connect to Jupyter notebook in your web browser:  http://jupyter.passian.federated
- Connect to TensorBoard in your web browser:  http://tensorboard.passian.federated

