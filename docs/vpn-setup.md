# Connecting to VPNs for PassianFL

You will need a VPN account to connect to PassianFL.
- Researchers need VPN access to the PassianFL Researcher Node network
- Data Providers need VPN access to their PassianFL Local Node network

If you require both roles, you will need separate VPN accounts for each network.

---

## Install the AWS Client VPN

PassianFL has been tested with the AWS Client VPN.
You can use other OpenVPN-compatible clients, but you will need to adjust the following 
instructions appropriately. 

You can install the 
[AWS Client VPN from the AWS website](https://aws.amazon.com/vpn/client-vpn-download)

---

## Obtain your VPN credentials

The administrator for your PassianFL Node should create your VPN
credentials following the [Adding users guide](adding-users.md).

The default PassianFL authorisation method is using certificates. For each VPN you need access to, 
your administrator will create a **client configuration file** for you and upload it to the AWS
Parameter Store. You need to download each client configuration file and add it to your AWS Client
VPN.

You can either download the contents each file directly, or use the `download_vpn_credentials.sh`
script.

---

### Download a personal client configuration file using the `download_vpn_credentials.sh` script

To use this script you must have the AWS CLI installed and your AWS profile set up as described in
the following pages:
- [Setting up a local machine](deployment-machine-setup.md)
- [Configure your AWS credentials](configure-aws-credentials.md)

From the terminal, navigate to the folder containing this repository and run
```bash
./scripts/download_vpn_credentials.sh <config-name> <node-name> <client-name> <aws-profile-name> 
```
where you must substitute:
- `<config-name>` with the configuration name for your deployment (e.g. `dev` or `prod`)
- `<node-name>` with `network` for the researcher node, or for local nodes it is the node name
(e.g. `nodea`) as specified in the section name of the configuration file
- `<client-name>` with the client name as used to generate the client certificate
- `<aws-profile-name>` with your local AWS credentials profile, e.g. `passian`  

Run this command for each VPN file you need to download. The files will be downloaded to 
the folder `~/passian_vpn_certificates/vpn_configuration_files`

---

### Download a personal client configuration file from the AWS Console

- Log into the AWS Console
- Go to AWS Systems Manager
- Select Parameter Store on the left
- There is a SecureString for each VPN - one for the Researcher VPN and one for each Data Node VPN
  - Click on a SecureString
  - Click View
  - Copy the contents into a local text file
  - Save securely with an appropriate name (eg `my_researcher_vpn_profile.ovpn`)
  - Repeat for the other SecureStrings

Note: on Linux you may need to add the line `dhcp-option DOMAIN-ROUTE .` to the start of the config 
file, if it is not already there.
See [Linux troubleshooting](https://docs.aws.amazon.com/vpn/latest/clientvpn-user/linux-troubleshooting.html)

---

## Add your VPN profiles to your VPN client
- Launch AWS VPN Client 
- Go to Manage Profiles
- Click `Add Profile`
- For `Display Name`, type in an appropriate name to help you identify the profile for this site, for example:
  - `PassianFL <site name> Researcher Node` for a Researcher Node
  - `PassianFL <site name> Local Node` for a Local Node
- For `VPN Configuration File`, select the file symbol and choose the client configuration file you downloaded for this site

  _Note: If you used the script to download your client configuration file, it will be in your home directory under `~/passian_vpn_certificates/vpn_configuration_files`_

- Repeat this process for each client configuration file. _Note: If you are a data provider for multiple sites, you need to add a profile for each site_

----

## Connect to the VPN

You can only connect to one VPN at a time. If you need to connect to multiple PassianFL networks,
close your existing VPN session before connecting to the next one.  

- Launch the AWS VPN Client 
- Select the appropriate profile:
  - If you are a Researcher, select the `Passian Researcher` profile
  - If you are a Data Provider, select the profile for your Data Node, for example `Passian Data Node (your site name)`
- Click `Connect`

---

## VPN Troubleshooting

See [Troubleshooting your Client VPN connection](https://docs.aws.amazon.com/vpn/latest/clientvpn-user/troubleshooting.html)
