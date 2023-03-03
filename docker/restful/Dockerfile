# UCL PASSIAN - Dockerfile for Fed-BioMed restful container

FROM --platform=linux/amd64 python:3.9-alpine
ENV PYTHONUNBUFFERED 1

# http restful server
EXPOSE 8000

# Copy files to container
COPY requirements.txt /requirements.txt
COPY ./entrypoint.bash /
COPY ./app /app

# Install dependencies
RUN apk update && apk add shadow bash
RUN apk add --no-cache --virtual .build-deps \
    ca-certificates gcc postgresql-dev linux-headers musl-dev \
    libffi-dev jpeg-dev zlib-dev bash \
    && pip install -r /requirements.txt

# Set working directory
WORKDIR /app

# Entrypoint script to be run on container launch
ENTRYPOINT ["/entrypoint.bash"]
