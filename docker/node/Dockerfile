# GPU support: NVIDIA base image and install
FROM --platform=linux/amd64 nvidia/cuda:11.5.0-base-ubuntu20.04

# Network env variables to be set at runtime
ENV MQTT_BROKER=""
ENV UPLOADS_URL=""

# install wget though nvidia cuda linux gpg key is obsolete
RUN apt-key del 7fa2af80 && apt-get update || true && apt install -y wget
# update nvidia cuda linux gpg repository key
# https://developer.nvidia.com/blog/updating-the-cuda-linux-gpg-repository-key/
RUN wget https://developer.download.nvidia.com/compute/cuda/repos/ubuntu2004/x86_64/cuda-keyring_1.0-1_all.deb && \
    dpkg -i cuda-keyring_1.0-1_all.deb && \
    sed -i '/developer\.download\.nvidia\.com\/compute\/cuda\/repos/d' /etc/apt/sources.list && \
    sed -i '/developer\.download\.nvidia\.com\/compute\/cuda\/repos/d' /etc/apt/sources.list.d/*
 \
# Install dependencies
# Python is required as it is not part of the base image
RUN apt-get update && apt-get install -y python3.9-full && \
    apt-get install -y iptables iproute2 iputils-ping bash vim net-tools procps build-essential kmod apt-utils wget rsync

# Install miniconda
RUN wget -q --directory-prefix=$HOME https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh && \
        bash $HOME/Miniconda3-latest-Linux-x86_64.sh -b -p /miniconda && \
        rm -f $HOME/Miniconda3-latest-Linux-x86_64.sh
ENV PATH=${PATH}:/miniconda/bin

# Conda initialisation for all users
RUN ln -s /miniconda/etc/profile.d/conda.sh /etc/profile.d/conda.sh

# Setup subset of fedbiomed code tree
RUN mkdir -p /fedbiomed/envs /data
COPY ./common/fedbiomed/envs/vpn /fedbiomed/envs/vpn
COPY ./common/fedbiomed/envs/common /fedbiomed/envs/common
COPY ./common/fedbiomed/envs/common /fedbiomed/envs/common_reference
COPY ./common/fedbiomed/fedbiomed /fedbiomed/fedbiomed
COPY ./common/fedbiomed/scripts /fedbiomed/scripts

# Copy entrypoint script
COPY ./node/entrypoint.bash /

# Append to bashrc for users starting interactive sessions
COPY ./node/bashrc_append /tmp
RUN cat /tmp/bashrc_append | tee -a /root/.bashrc /root/bashrc_entrypoint \
        /etc/skel/.bashrc /etc/skel/bashrc_entrypoint >/dev/null

# Set working directory
WORKDIR /fedbiomed

# Install dependencies from conda environment file
RUN conda env update --file ./envs/vpn/conda/fedbiomed-node.yaml && \
    pip cache purge && conda clean -a -y

# Entrypoint script to be run on container launch
ENTRYPOINT ["/entrypoint.bash"]

