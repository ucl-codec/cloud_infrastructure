# Adding users

Adding a user requires creating the appropriate accounts or credentials for them, depending on
the role they need to perform

---

## Adding researchers
- Create VPN credentials for the Researcher Node 

---

## Adding data providers
- Add an AWS IAM account giving the user access to their Local Node S3 import bucket

  _This allows data providers to upload data to the S3 import bucket of their local node_

- Create VPN credentials for their Local Node.

  _This allows users to connect to the Fed Bio-Med gui on their local node_

- Add an account on their Local Node Fed-BioMed GUI.

  _This allows users to log into the Fed-BioMed gui on their local node to tag datasets and approve training plans_

---

## Creating VPN credentials

VPN connections use certificate-based authentication by default.

Each user is provided with a VPN _client configuration file_ for each VPN they need to connect to.
The client configuration file contains the connection details for the VPN and the user's private
key and certificate for that VPN. This file must be kept secure. 
The user will load this file into the AWS Client VPN or compatible OpenVPN client software. 

The Researcher Node and each of the Local Nodes each have their own separate VPNs. If a user needs
to connect to multiple VPNs, they will require a separate client configuration file for each one.

You can assemble the client configuration file by hand, or use the script provided.

---

### Using the `create_vpn_client.sh` script

`create_vpn_client.sh` must be run on the same machine which you originally used to initialise the 
VPN using the `initialise.sh` script. This is because it requires the CA private keys.

Run the script using:
```bash
./scripts/create_vpn_client.sh <config-name> <node-name> <client-name> <aws-credentials-profile>
```
where you need to set the parameters as follows:
- `<config-name>`: name of the config file describing this PassianFL system (in the `config` folder), such as `dev` or `prod`
- `<node-name>`: is `network` for the researcher node, or the node name for a local node. The node name is the section name of the part of the config file which describes that node, e.g. `nodea`
- `<client-name>` is the user or machine name which identifies the user of the certificate. The certificate will be given a CN of the form `<client-name>.<node-name>.<config-name> (note this does not have to correspond to their machine's DNS name)
- `<aws-credentials-profile>` is the name of your local AWS profile containing AWS credentials, e.g. `passian`

The script will:
- generate and save a new client certificate under `~/passian_vpn_certificates`
- upload the client certificate to the AWS Certificate Store
- generate a client configuration file and store it as a SecureString AWS Parameter in the AWS Parameter Store under the name `<config-name>-<node-name>-<client-name>-vpn-profile`

The user can access the SecureString parameter and download to a local file, which they can import into the AWS Client VPN.  


---

### Manually assembling VPN client configuration files

- Download the `client configuration` from the appropriate Client VPN Endpoint on the AWS VPC console
- In the downloaded file, add in a `<cert></cert>` section containing the user's certificate, and a `<key></key>` section 
containing the user's key
