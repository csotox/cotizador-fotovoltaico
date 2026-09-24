
ingresar:
	clear
	docker exec -it --user vscode cf-dev-ia bash

run-server:
	# Servidor de desarrollo (base de datos de desarrollo). NO usar para ejecutar tests.
	python ./cotizacion/manage.py runserver 0.0.0.0:8000

test:
	pytest

# Ejecuta los tests E2E usando la fixture live_server (base de datos de test).
# No requiere un servidor externo levantado.
test-e2e:
	pytest -m e2e
