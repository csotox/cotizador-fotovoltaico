# Guía de implementación de Servidor VPS

---

## Seleccionar proveedor de VPS

- Buscar su proveedor de confianza
- Contratar el VPS según sus requerimientos.

### OVH

- Al contratar envia un correo electrónico, que debemos buscar el enlace para generar el Password.
- Luego ingresamos vía ssh desde la terminal de nuestro host local a la ip suministrada para el vps.
~~~ bash
ssh ubuntu@<ip-vps>
~~~

---

## Primeros paso

### 1.1 - Actualizar el servidor

~~~ bash
sudo apt update && sudo apt upgrade -y
~~~

### 1.2 - Reiniciar el servidor

~~~ bash
sudo reboot
~~~

### 1.3 - Configurar zona horaria

~~~ bash
sudo timedatectl set-timezone America/Santiago
~~~

---

## Seguridad del servidor

### 2.1 - Instalación y configuración de `ufw`

~~~ bash
sudo apt install ufw -y
~~~

~~~ bash
sudo ufw default deny incoming
~~~

~~~ bash
sudo ufw default allow outgoing
~~~

~~~ bash
sudo ufw allow 22/tcp
~~~

~~~ bash
sudo ufw allow 80/tcp
~~~

~~~ bash
sudo ufw allow 443/tcp
~~~

### NOTA: Deben estar abiertos los puertos 22, 80 y 443. Antes del siguiente paso

~~~ bash
sudo ufw enable
~~~

~~~ bash
sudo ufw status verbose
~~~

### `fail2ban`

~~~ bash
sudo apt install fail2ban -y
~~~

~~~ bash
sudo systemctl enable fail2ban
~~~

~~~ bash
sudo systemctl start fail2ban
~~~

- Status

~~~ bash
sudo fail2ban-client status sshd
~~~


---

## Docker

- Dependencias iniciales

~~~ bash
sudo apt install ca-certificates curl gnupg -y
~~~

~~~ bash
sudo install -m 0755 -d /etc/apt/keyrings
~~~

~~~ bash
sudo curl -fsSL https://download.docker.com/linux/ubuntu/gpg -o /etc/apt/keyrings/docker.asc
~~~

~~~ bash
sudo chmod a+r /etc/apt/keyrings/docker.asc
~~~

~~~ bash
sudo tee /etc/apt/sources.list.d/docker.sources <<EOF
Types: deb
URIs: https://download.docker.com/linux/ubuntu
Suites: $(. /etc/os-release && echo "${UBUNTU_CODENAME:-$VERSION_CODENAME}")
Components: stable
Architectures: $(dpkg --print-architecture)
Signed-By: /etc/apt/keyrings/docker.asc
EOF
~~~

~~~ bash
sudo apt update
~~~

### Instalación de Docker

~~~ bash
sudo apt install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin
~~~

### Activar y configurar

~~~ bash
sudo systemctl enable docker
~~~

~~~ bash
sudo systemctl start docker
~~~

### Usuario Docker

~~~ bash
sudo usermod -aG docker ubuntu
~~~

~~~ bash
newgrp docker
~~~

### Validar instalación

~~~ bash
docker --version
~~~

~~~ bash
docker compose version
~~~

### Habilitar Docker con el inicio del Servidor

~~~ bash
sudo systemctl enable docker
~~~

~~~ bash
sudo systemctl enable containerd
~~~

---

## Dokploy

~~~ bash
curl -sSL https://dokploy.com/install.sh | sudo sh
~~~

### Verificar la instalación

~~~ bash
sudo ss -tulpn | grep 3000
~~~

---

# Deploy de la aplicación

La imagen se construye con el `Dockerfile` de la raíz (Python 3.13 + Gunicorn + WhiteNoise).
El stack se define en `docker-compose.prod.yml` y expone solo el servicio `web`
(puerto interno `8000`). Traefik/Dokploy termina el TLS y enruta el dominio.

## Archivos

- `Dockerfile` — imagen de producción (build multi-stage, usuario sin privilegios).
- `docker-compose.prod.yml` — servicio `web` (Gunicorn) + `postgres` en red interna.
- `docker/entrypoint.sh` — aplica migraciones, crea superusuario y collectstatic, luego lanza Gunicorn.
- `.env.prod.example` — variables de entorno. Copiar a `.env.prod` y completar.

## Preparar el entorno

~~~ bash
cp .env.prod.example .env.prod
python -c "import secrets; print(secrets.token_urlsafe(64))"
~~~

- `SECRET_KEY`: salida del comando anterior.
- `ALLOWED_HOSTS`: dominio real, sin `https://` ni barra final.
- `CSRF_TRUSTED_ORIGINS`: `https://` + dominio real.
- `POSTGRES_PASSWORD`: contraseña de la base de datos.
- `DJANGO_SUPERUSER_*`: opcional, solo se usa en el primer deploy.

## Levantar el stack

~~~ bash
docker compose -f docker-compose.prod.yml build
docker compose -f docker-compose.prod.yml up -d
~~~

Ver estado y logs:

~~~ bash
docker compose -f docker-compose.prod.yml ps
docker compose -f docker-compose.prod.yml logs -f web
~~~

## Deploy en Dokploy

1. Crear un recurso **Compose**.
2. Definir el repositorio y el archivo Compose: `docker-compose.prod.yml`.
3. Cargar las variables de entorno en la sección **Environment** (o usar `.env.prod`).
4. En la pestaña **Domains** asociar el dominio y apuntar al servicio `web`, puerto `8000`.
   Dokploy genera las etiquetas de Traefik automáticamente.
5. Desplegar. `ALLOWED_HOSTS` y `CSRF_TRUSTED_ORIGINS` deben coincidir con ese dominio.

## Backups

~~~ bash
docker compose -f docker-compose.prod.yml exec postgres \
  pg_dump -U cotizador -Fc cotizador > backup_$(date +%F).dump
~~~

## Actualizar el deploy

~~~ bash
git pull
docker compose -f docker-compose.prod.yml build
docker compose -f docker-compose.prod.yml up -d
~~~

## Notas

- La base de datos no publica puertos; solo es accesible dentro del compose.
- Los archivos estáticos los sirve WhiteNoise desde el contenedor `web`, con hash de caché.
- `DEBUG`, `SECRET_KEY`, `ALLOWED_HOSTS` y cookies seguras se leen del entorno;
  los valores por defecto de `settings.py` son solo para desarrollo.

