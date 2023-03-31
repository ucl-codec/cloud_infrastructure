# Development guide for PassianFL

---

## Configuring your machine for local development

- The base requirements are the same as in the [Deployment machine setup](deployment-machine-setup.md).
- Additional python dependencies are in `requirements-dev.txt`


---

## Multiple configurations for test/staging/production etc 

Use [Configuration files](configuration-files.md) to create different PassianFL environments
- CDK deployments are independent if they have different Stack Names. You can ensure this by providing unique stack prefixes in the configuration
- Some AWS resources gave global names, such as S3 buckets and parameters. You need to specify 
- non-conflicting names in the configuration files for these. But you can share these resources if you wish to between configurations. 

Note that the provided "production" template requires 3 VPCs, and the provided "development" template requires 2.
The initial VPC limit in each AWS account is 5 VPCs, but you can request that AWS increase this.

---

## Stack architecture

- See [Architecture](architecture.md)

---

## Fork of Fed-BioMed

A custom fork of Fed-BioMed is included as a submodule.
To update the version of Fed-BioMed that will be deployed:
- Update the custom fork of Fed-BioMed, merging in changes from the main repository and your custom changes as required
- Update the git submodule reference in this repository



---

## Local docker testing 

You can locally run the PassianFL docker containers on your machine for testing.
See [Local docker testing](local-docker-testing.md).

---

## Unit tests

- see [Unit tests](unit-tests.md)
