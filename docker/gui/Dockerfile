# UCL PASSIAN - Dockerfile for Fed-BioMed gui container

FROM --platform=linux/amd64 debian:bullseye-slim

# Port used by flask server
ARG GUI_PORT_DEFAULT=8484

# Note the actual port used can be overridden at runtime using environment variables
EXPOSE ${GUI_PORT_DEFAULT}

# Initial GUI configuration - can be set at runtime by specifying env variables
ENV GUI_HOST=localhost
ENV GUI_PORT=${GUI_PORT_DEFAULT}
ENV GUI_DATA_PATH=/data
ENV GUI_DEFAULT_ADMIN_EMAIL=admin@fedbiomed.gui
ENV GUI_DEFAULT_ADMIN_PW=admin
ENV GUI_TIMEOUT=600

# Install dependencies
RUN apt-get update && apt-get install -y apt-utils wget procps gettext-base

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
COPY ./common/fedbiomed/gui /fedbiomed/gui



# Set working directory
WORKDIR /fedbiomed

# Install dependencies from conda environment file
RUN conda env update --file ./envs/vpn/conda/fedbiomed-gui.yaml && \
	pip cache purge && conda clean -a -y

# Install the gui but do not run. `data-folder` and `config` are not used when doing `install-only`
RUN ./scripts/fedbiomed_run gui data-folder /data config DUMMY install-only start

# Move the GUI build to a root folder, as /fedbiomed/var will be overwritten by a mount when the
# container is run
RUN mv /fedbiomed/var/gui-build /gui-build

# Copy entrypoint script
COPY ./gui/entrypoint.bash /

# Copy GUI config file template to image. This will be used in the entrypoint script
COPY ./gui/config_gui.ini.template /

# Entrypoint script to be run on container launch
ENTRYPOINT ["/entrypoint.bash"]
