
ingresar:
	clear
	docker exec -it --user vscode cf-dev-ia bash

run-server:
	python ./cotizacion/manage.py runserver 0.0.0.0:8000

test:
	pytest

# Requiere un servidor en vivo (usa la base de datos real):
test-e2e:
	pytest -m e2e
