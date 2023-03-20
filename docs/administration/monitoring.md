# Monitoring

---

## CloudWatch logs

AWS services including the Fargate and EC2 services, data sync and VPN connections send logs to
CloudWatch. Logs are stored in log groups and typically preserved for 1 at least 1 day even if the 
service is shut down, to allow for troubleshooting.

You can find direct links from the AWS services. For example, to find the logs for the FBM node
service:
- Launch the AWS Console
- Go to Elastic Container Service
- Click on the local node cluster (e.g. `FbmNodeAServiceStack-Clusterxxxxxxx`)
- Click on the Node service (e.g. `FbmNodeAServiceStack-NodeServiceEc2Servicexxxxxxx`) 
- Click on the `Logs` tab
- Click on `View in CloudWatch`


---

## Start a remote shell on the node instances using Session Manager

The Fed-BioMed Node service runs on an GPU-enabled EC2 instance. You can connect to this using
AWS Session Manager from within the AWS Console
- [See here for details](https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/session-manager.html)

Note you can navigate directly to an EC2 node instance from the Elastic Container Services page. To
do this select the appropriate Node Services Stack cluster, select the Instances tab, then click on 
the Instance ID listed in the Container Instances section at the bottom. 