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
El stack se define en `docker-compose.prod.yml`; el servicio `web` escucha en el puerto
interno `8000` y PostgreSQL no publica puertos. Dokploy/Traefik termina el TLS y enruta
el dominio al servicio `web`.

## Archivos

- `Dockerfile` — imagen de producción (build multi-stage, usuario sin privilegios).
- `docker-compose.prod.yml` — servicio `web` (Gunicorn) + `postgres`; las variables se leen del entorno de Compose/Dokploy.
- `docker/entrypoint.sh` — aplica migraciones, crea superusuario opcional y lanza Gunicorn.
- `.env.prod.example` — variables de entorno. Copiar a `.env.prod` y completar.

## Preparar el entorno

~~~ bash
cp .env.prod.example .env.prod
python -c "import secrets; print(secrets.token_urlsafe(64))"
~~~

- `SECRET_KEY`: salida del comando anterior.
- `ALLOWED_HOSTS`: dominio real, sin `https://` ni barra final.
- `CSRF_TRUSTED_ORIGINS`: `https://` + dominio real.
- `POSTGRES_PASSWORD`: contraseña aleatoria de la base de datos (por ejemplo, `openssl rand -hex 32`).
- `DJANGO_SUPERUSER_*`: opcional, solo se usa en el primer deploy.

## Levantar el stack manualmente

~~~ bash
docker compose --env-file .env.prod -f docker-compose.prod.yml up -d --build
~~~

Ver estado y logs:

~~~ bash
docker compose --env-file .env.prod -f docker-compose.prod.yml ps
docker compose --env-file .env.prod -f docker-compose.prod.yml logs -f web
~~~

## Deploy en Dokploy + Traefik

1. Apuntar el registro DNS `A` del dominio a la IP pública del VPS (y `AAAA` si el VPS usa IPv6).
2. En Dokploy crear una aplicación de tipo **Docker Compose** desde este repositorio y seleccionar `docker-compose.prod.yml`.
3. En **Environment**, agregar las variables de `.env.prod.example`. No cargar el archivo `.env.prod` como archivo requerido por el stack: Dokploy inyecta las variables configuradas y Compose las pasa explícitamente a cada servicio.
4. Reemplazar `cotizador.example.cl` por el dominio real en `ALLOWED_HOSTS` y `CSRF_TRUSTED_ORIGINS` (`https://dominio`). Completar `SECRET_KEY` y `POSTGRES_PASSWORD` con valores aleatorios.
5. En **Domains**, crear un dominio para el servicio `web`, puerto de contenedor `8000`, activar HTTPS y seleccionar Let's Encrypt.
6. Dokploy agrega la configuración de Traefik y conecta `web` a la red del proxy. No se publican puertos del host en el Compose.
7. Desplegar/redeploy. Confirmar en Dokploy que DNS resuelve al VPS y que los puertos `80/tcp` y `443/tcp` están abiertos en firewall/proveedor.

No es necesario agregar labels manuales de Traefik: para un Compose de Dokploy se recomienda configurar el dominio en la pestaña **Domains**. `expose: 8000` permite que Traefik enrute al contenedor sin publicar el puerto en el VPS.

## Backups

~~~ bash
docker compose --env-file .env.prod -f docker-compose.prod.yml exec postgres \
  pg_dump -U cotizador -Fc cotizador > backup_$(date +%F).dump
~~~

## Actualizar el deploy

~~~ bash
git pull
docker compose --env-file .env.prod -f docker-compose.prod.yml up -d --build
~~~

## Notas

- La base de datos no publica puertos; solo es accesible desde los servicios del stack.
- Los archivos estáticos se recopilan durante el build y WhiteNoise los sirve desde el contenedor `web`, con hash de caché.
- `DEBUG`, `SECRET_KEY`, `ALLOWED_HOSTS` y cookies seguras se leen del entorno;
  los valores por defecto de `settings.py` son solo para desarrollo.
