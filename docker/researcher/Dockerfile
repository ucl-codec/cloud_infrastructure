# UCL PASSIAN - Dockerfile for Fed-BioMed researcher container

FROM --platform=linux/amd64 python:3.9-slim-bullseye

# Jupyter notebook
EXPOSE 8888

# tensorboard via socat proxy
EXPOSE 6007

# Install dependencies
RUN apt-get update && apt-get install -y apt-utils wget socat

# Install miniconda
RUN wget -q --directory-prefix=$HOME https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh && \
        bash $HOME/Miniconda3-latest-Linux-x86_64.sh -b -p /miniconda && \
        rm -f $HOME/Miniconda3-latest-Linux-x86_64.sh
ENV PATH=${PATH}:/miniconda/bin

# Setup subset of fedbiomed code tree
RUN mkdir -p /fedbiomed/envs /data
COPY ./common/fedbiomed/envs/vpn /fedbiomed/envs/vpn
COPY ./common/fedbiomed/fedbiomed /fedbiomed/fedbiomed
COPY ./common/fedbiomed/scripts /fedbiomed/scripts
COPY ./common/fedbiomed/notebooks /fedbiomed/notebooks

# Copy entrypoint script
COPY ./researcher/entrypoint.bash /

COPY ./researcher/bashrc_append /tmp
RUN cat /tmp/bashrc_append | tee -a /root/.bashrc /root/bashrc_entrypoint \
        /etc/skel/.bashrc /etc/skel/bashrc_entrypoint >/dev/null

RUN ln -s /miniconda/etc/profile.d/conda.sh /etc/profile.d/conda.sh

# Set working directory
WORKDIR /fedbiomed

# Install dependencies from conda environment file
RUN conda env update --file ./envs/vpn/conda/fedbiomed-researcher.yaml && \
	pip cache purge && conda clean -a -y 

# Entrypoint script to be run on container launch
ENTRYPOINT ["/entrypoint.bash"]
