# UCL PASSIAN - Dockerfile for Fed-BioMed gui container

FROM debian:bullseye-slim

# flask server
EXPOSE 8484

# Initial GUI configuration - can be set at runtime by specifying env variables
ENV GUI_HOST=localhost
ENV GUI_PORT=8484
ENV GUI_DATA_PATH=/data
ENV GUI_DEFAULT_ADMIN_EMAIL=admin@fedbiomed.gui
ENV GUI_DEFAULT_ADMIN_PW=admin

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

# Copy GUI config file template to image. This will be used in the entrypoint script
COPY ./gui/config_gui.ini.template /

# Copy entrypoint script
COPY ./gui/entrypoint.bash /

# Set working directory
WORKDIR /fedbiomed

# Install dependencies from conda environment file
RUN conda env update --file ./envs/vpn/conda/fedbiomed-gui.yaml && \
	pip cache purge && conda clean -a -y

# Install the gui but do not run. `data-folder` and `config` are not used when doing `install-only`
RUN ./scripts/fedbiomed_run gui data-folder /data config DUMMY install-only start

# Entrypoint script to be run on container launch
ENTRYPOINT ["/entrypoint.bash"]
