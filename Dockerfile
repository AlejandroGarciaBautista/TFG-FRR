# Usa una imagen base ligera de Debian con Python 3
FROM python:3.11-slim

# Evita preguntas interactivas y actualiza repositorios
ENV DEBIAN_FRONTEND=noninteractive

# Instala dependencias del sistema necesarias para Ansible, Docker-CLI y Python libs
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
      sshpass \
      libssl-dev \
      libffi-dev \
      build-essential \
      docker.io \
      python3-pip && \
    rm -rf /var/lib/apt/lists/*

# Instala Ansible y librerías Python necesarias (requests y docker SDK)
RUN pip install --no-cache-dir ansible requests docker

# Directorio de trabajo para tus playbooks
WORKDIR /ansible

# Copia opcional de tus playbooks/inventarios
# COPY inventory.yml playbook.yml /ansible/

# Para que el contenedor no termine, dejamos este comando en foreground
CMD ["tail", "-f", "/dev/null"]
