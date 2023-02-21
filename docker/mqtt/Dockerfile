# UCL PASSIAN - Dockerfile for Fed-BioMed mqtt container

FROM eclipse-mosquitto

# MQTT port
EXPOSE 1883

# Entrypoint command to be run on container launch
ENTRYPOINT [ "/usr/sbin/mosquitto", "-c", "/mosquitto-no-auth.conf" ]
