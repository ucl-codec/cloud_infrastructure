# User guide for PassianFL

This guide is for end users of PassianFL. It assumes you have a fully working installation
of PassianFL on AWS.

Users may be  
- Researchers: can execute federated training
- Data Providers: can add data to their Data Nodes and approve use of training plans on their data

If you have both of these roles, you need to consider role independently when following the following instructions.

---

## Data Provider 

### Add data

- You can upload data using the AWS S3 import bucket for your Local Node.
- You will need an AWS IAM account provided by your system administrator with access to this bucket.
- You can use this to upload data using the AWS S3 web interface or command line
- After upload, data will be synced form the S3 bucket into the Local Node.
  - Synchronisation starts once per hour, so after adding data you may have to wait before the data
become available on the node
  - The PassianFL Local Node administrator can manually trigger an immediate sync from the AWS Data Sync console. See [Data sync](data-sync.md)   
  - Data sync can take some time depending on the size of the data 
    - Data deleted from the S3 bucket will also be deleted from the Local Node during the sync

### Set up your VPN access

- See [Connecting to VPNs for PassianFL](vpn-setup.md)

### Connect to your Data Node

- Launch the AWS VPN Client 
- Select the VPN profile for your Local Node:
  - for example `Passian Data Node (your site name)`
- Click `Connect`
- Connect to Fed Bio-Med GUI in your web browser:
  - Site A: http://gui.passian.clinicala
  - Site B: http://gui.passian.clinicalb
  - NOTE: these URLs will depend on the configuration of your system: see [Configuration files](configuration-files.md)


### Log into the Fed-BioMed gui
The Fed-BioMed gui has its own accounts. Your will need your PassianFL system administator to 
create an account for you and provide you with the credentials 


### Tag datasets

Once data have fully arrived on the Local Node, you need to add and tag the data using the
Fed Bio-Med gui. This allows a researcher to request a training plan to be run on the data.
See the Fed-BioMed documentation for details.

### Approve training plans
You will need to approve a researcher's training plans before they can be run on your data.
See Fed-BioMed documentation for details.

---

## Researcher

### Set up your VPN access

- See [Connecting to VPNs for PassianFL](vpn-setup.md)

### Connect to the Researcher network
- Launch the AWS VPN Client 
- Select your `Passian Researcher` profile
- Click `Connect`
- Connect to Jupyter notebook in your web browser:  http://jupyter.passian.federated
- Connect to TensorBoard in your web browser:  http://tensorboard.passian.federated

See Fed-BioMed documentation for examples of how to use Jupyter notebooks with Fed-Biomed.
