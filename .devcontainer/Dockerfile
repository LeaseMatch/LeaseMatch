# Usar la imagen base de Python 3.9
FROM python:3.9-slim

# Configurar ambiente de instalación
ENV DEBIAN_FRONTEND=noninteractive

# Actualizar repositorios e instalar dependencias esenciales
RUN apt-get update && apt-get install -y \
    curl \
    git \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Instalar paquetes Python requeridos
RUN pip install --no-cache-dir \
    aws-cdk-lib>=2.0.0 \
    constructs>=10.0.0 \
    boto3==1.34.125 \
    black

# Instalar Node.js y AWS CDK CLI
RUN curl -sL https://deb.nodesource.com/setup_18.x | bash - && \
    apt-get install -y nodejs && \
    npm install -g aws-cdk @aws-sdk/client-s3 --unsafe-perm=true && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Establecer el directorio de trabajo
WORKDIR /workspace

# Configurar el contenedor para iniciar con bash
CMD ["bash"]
