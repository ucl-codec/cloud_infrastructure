# Troubleshooting

---

## CDK / CloudFormation issues

### Drift

CDK/CloudFormation expect to manage the AWS resources they create. If resources are manually 
added, modified or deleted, this can result in stack drift and CDK may be unable to perform updates.

For example, if you manually create an AWS resource that depends on a VPC, then
CloudFormation may be unable to modify that VPC because of the dependency you have created.

Drift can be fixed by reverting manual changes, creating and importing missing resources, or
by deleting CloudFormation stacks. AWS provides tools to detect and analyse drift. 
- [AWS documentation on stack drift](https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/using-cfn-stack-drift.html)  


### Update failures

In some cases CloudFormation updates resources by creating a new resource and then deleting
the old one. This can sometimes fail because of dependency ordering (the old resource cannot be 
deleted as it is still in use by another resource) or because of unique naming constraints (e.g. 
a new S3 bucket cannot be created with the same name as an exiting bucket).

In some cases you may find it easier to delete the stacks that are causing update issues. You 
may need to manually delete resources which CloudFormation cannot delete and which are causing
conflicts.



---

## Docker errors

- Can't connect to docker daemon. Is 'docker -d' running on this host?

This is likely because you haven't installed a Docker engine, or it is not currently running.

On macOS/Windows, you can install a Docker engine by installing Docker Desktop or compatible 
alternatives such as Rancher Desktop or Colima. Note this in addition to installing the Docker command line.
The Engine provides a linux VM where Docker actually runs the builds

If your docker engine is not set to launch automatically, you can launch it by running the Docker 
Desktop or Rancher Desktop gui, or using the appropriate command-line calls.  

## Errors during Docker container building

Common intermittent build errors are due to the Docker engine having insufficient RAM or disk space.
You can adjust the RAM and disk space in the engine's settings.
 - In Docker Desktop, launch the GUI and go to Settings/Resources.

## No space left on device

This refers to the disk space available to the Docker engine. You can increase this through the
engine's settings as described above.

In addition, old images and volumes may fill up your engine's disk space. To reclaim space, use docker prune 
commands. Note however that pruning may increase build time or force a complete rebuild 

Example commands (see docker documentation for more details)
- Remove unused images: `docker system prune`
- Remove all images: `docker system prune --all --force`
- Remove all docker volumes: `docker system prune --all --force --volumes`

## exit code: 13

`exit code: 13` during a local docker build indicates you need to increase the maximum RAM 
available to the local docker VM. You can adjust the RAM and disk space in the engine's settings 
as described above



---
