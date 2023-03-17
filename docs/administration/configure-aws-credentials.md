# Configure your AWS credentials

---

To use the AWS and CDK command-line tools, you require credentials.
You can obtain temporary credentials (recommended) or an AWS access key.
If you use te temporary credentials, you will need to update these periodically when they expire.

---
# Obtain credentials

### Temporary credentials

These can be obtained from the IAM Identity Centre (if you have access), or through the AWS command-line

### Create an AWS Access Key
- You can do this on the AWS Console: https://docs.aws.amazon.com/IAM/latest/UserGuide/id_credentials_access-keys.html

---

## Add credentials to your machine

It is recommended not to configure default credentials, but instead create a dedicated profile called `passian`.
This prevents issues with accidently deploying to the wrong account when you have access to multiple AWS accounts.  

### Create an AWS named profile on your machine, named `passian`
```bash
aws configure --profile passian 
```
This will create entries in `~/.aws/credentials` and `~/.aws/config`. Alternately, you can set 
these up manually. For more details, see https://docs.aws.amazon.com/cli/latest/userguide/cli-configure-profiles.html


---
