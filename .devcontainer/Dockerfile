FROM python:3.13-slim

WORKDIR /workspace

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PIP_DISABLE_PIP_VERSION_CHECK=1

RUN apt-get update && apt-get install -y --no-install-recommends \
    cloc \
    bash \
    git \
    curl \
    wget \
    tree \
    htop \
    sudo \
    ripgrep \
    build-essential \
    ca-certificates \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Instalar Node.js
RUN curl -fsSL https://deb.nodesource.com/setup_22.x | bash - \
    && apt-get install -y nodejs \
    && rm -rf /var/lib/apt/lists/*

# Instalar Pyright
RUN npm install -g pyright

# Requirements.txt
COPY ./.devcontainer/requirements.txt .

RUN python -m pip install --upgrade pip setuptools wheel \
    && pip install --no-cache-dir -r requirements.txt

# Crear usuario vscode
RUN useradd -m -s /bin/bash vscode \
    && echo "vscode ALL=(ALL) NOPASSWD:ALL" > /etc/sudoers.d/vscode \
    && chmod 0440 /etc/sudoers.d/vscode

USER vscode

# Instalar OpenCode
RUN curl -fsSL https://opencode.ai/install | bash \
    && /home/vscode/.opencode/bin/opencode --version

ENV PATH="/home/vscode/.opencode/bin:${PATH}"

CMD ["bash"]
