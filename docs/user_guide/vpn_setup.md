# Setting up the VPN

You will need a VPN account to connect to Passian Learning.
- Researchers need VPN access to the Passian Learning Researcher network
- Data Providers need VPN access to their Passian Learning Data Node network

If you require both roles, you will need separate VPN accounts for each network.

---

## Install the AWS Client VPN

Passian Learning has been tested with the AWS Client VPN.
You can use other OpenVPN-comaptible clients, but you will need to adjust the following 
instructions appropriately. 

You can install the [AWS Client VPN from the AWS website](https://aws.amazon.com/vpn/client-vpn-download)

---

## Obtain your VPN profiles

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
- If you are a researcher, add your Researcher profile with profile name `Passian Researcher`
- If you are a data provider, add your Data Node profile with profile name `Passian Data Node (your site name)`.
  - _Note: If you are a data provider for multiple sites, you need to add a profile for each site_

----

## Connect to the VPN

You can only connect to one VPN at a time. If you need to connect to multiple PASSIAN-FL networks,
close your existing VPN session before connecting to the next one.  

- Launch the AWS VPN Client 
- Select the appropriate profile:
  - If you are a Researcher, select the `Passian Researcher` profile
  - If you are a Data Provider, select the profile for your Data Node, for example `Passian Data Node (your site name)`
- Click `Connect`

---

## VPN Troubleshooting

See [Troubleshooting your Client VPN connection](https://docs.aws.amazon.com/vpn/latest/clientvpn-user/linux-troubleshooting.htmlhttps://docs.aws.amazon.com/vpn/latest/clientvpn-user/troubleshooting.html)

