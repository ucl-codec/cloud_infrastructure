# Teardown

The simplest way to remove a PassianFL aws installation is to delete the CloudFormation stacks.
Some of these will need to have termination protection removed before you can delete them.

After deleting the stacks, you may also need to manually remove resources that cannot be deleted or 
which were not created by CloudFormation.

Do not delete resources manually, as you may then be unable to perform further CDK updates.


---
## Disable deletion protection

The following stacks have termination protection enabled:
- passian-(config-name)-network-NetworkStack
- passian-(config-name)-(node-name)-NodeStack
- passian-(config-name)-(node-name)-DataImportStack

Here, (config-name) is the name of your configuration (e.g. dev or prod) and (node-name) is the
name of the local node (each local node has its own stacks).

In order to delete these stacks, you must remove termination protection

- Log into the AWS Console
- Go to CloudFormation > Stacks
- For each stack:
  - Click the radio button next to the stack
  - Click `Stack actions` > `Edit termination protection`
  - Select `Disabled`
  - Click Save

---

## Destroy the CDK stack

Once you have disabled termination protection, there are several ways you can delete the stacks: 
- Using the convenience scripts (see below) on the command line;
- Deleting the CloudFormation stacks on the AWS Console;
- From the command line using `cdk destroy` 


You should only manually delete resources in one of following situations:
 - they were created outside of CDK (such as by the `initialise.sh` script above)
 - where the stack has already been destroyed and a resource remains because it could not be deleted

Some stacks have been protected from deletion. This is because they contain "stateful" resources
(such as the file systems and VPN). Destroying these could result in data loss or users having to 
obtain new VPN credentials. To remove protected stacks, you will first need to disable stack
protection, which can be done using the AWS console. 

Convenience scripts are provided for destroying the dev stack:
```bash
./scripts/destroy_dev.sh
```
and for destroying the production stack:
```bash
./scripts/destroy_prod.sh
```

Note that resources defined outside of the CDK stacks will not be deleted (such as the VPN 
certificates, and the parent public hosted zone if you are using https). Additionally,
some resources may not delete as they are protected from deletion (such as S3 buckets logs) or are
in use by other resources. These can be deleted manually after the rest of the stack deletion is 
complete.

You might not be able to re-deploy a deleted stack if fixed-name resources (such as S3 buckets) have
not been deleted.

Any resources that are not deleted will continue to incur the relevant AWS costs. 

