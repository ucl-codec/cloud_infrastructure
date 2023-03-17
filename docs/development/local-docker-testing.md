# Local docker testing 

You can build and run the PassianFL docker containers on your local machine using the helper 
scripts. This will give you a fully working test Fed-BioMed instance on your local machine.

---
## Requirements

Please configure your system as described in [Deployment machine setup](../administration/deployment-machine-setup.md).
You don't need to install AWS tools or credentials, but you do need to install a docker engine and 
configure its RAM and disk limits so that you can build and run the containers

---

## Build the docker files on your local machine
```bash
./local_development/local_docker_build.sh
```

---

## Run the docker files on your local machine
```bash
./local_development/local_docker_run.sh
```

If the build and run succeed, you should be able to access the containers via localhost:
  - Fed-BioMed Node gui: http://localhost:8484
  - Jupyter notebook: http://localhost:8888
  - TensorBoard: http://localhost:6007

---

## SSH into the docker containers while they are running
```bash
docker exec -it node bash
docker exec -it researcher bash
docker exec -it gui bash
docker exec -it mqtt bash
docker exec -it restful bash
```

---

## Destroy the containers
```bash
./local_development/local_docker_destroy.sh
```

Note you may need to manually remove persistent files and docker images to reclaim disk space 

---

## Development notes

### Persistent files

Persistent files (data etc.) for the Docker deployment are stored in `.local_docker_storage`. You 
may wish to delete this folder after destroying the containers in order to reclaim disk space.

You may also wish to delete `.local_docker_storage` to simulate a clean install. 

### Environment variables

Some configuration is set via environment variables in the `local_docker_run.sh` script. You can
modify these values but you will need to destroy and re-run the containers for them to be recognised.

### Reclaim disk space using docker prune 

To force reclaim docker disk space, removing containers, images and volumes:
```bash
docker system prune --all --force --volumes
```

---
## Troubleshooting

See [Troubleshooting](../administration/troubleshooting.md)

