# Managing instances and services

You can temporarily disable services to reduce aws running costs when the system is not in use.

The current Fed-BioMed architecture does not support doing this automatically on-demand, but you
can manually disable or re-enable the services using the AWS Console.

To modify services, first find the appropriate cluster on the AWS Console: 
- Log onto the AWS Console
- Go to Elastic Container Service
- Click on the cluster containing the service(s) you wish to modify
  - The Researcher Service Stack contains the Jupyter amd Tensorboard services
  - The Node Service Stacks contain the FBM gui and FBM node services. There is one stack for each local node

To temporarily disable services:
- Under the Services tab, tick the service you wish to modify
- Click `Update`
- Change `Desired tasks` to 0
- Click `Update`

To re-enable services you previously disabled:
- Under the Services tab, tick the service you wish to modify
- Click `Update`
- Change `Desired tasks` to 1
- Click `Update`

Note: it may take 5 mins or more for services to fully shut down or start up.

## Shutting down GPU instances

If you shut down the Node Service following the above instructions (by setting the desired tasks to 
zero), the GPU-enabled EC2 instance will automatically shut down 15 minutes later and still stop 
incurring charges.

Setting the desired tasks back to 1 will cause a new instance to start. This can take around 5 minutes.


