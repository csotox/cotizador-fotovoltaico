
ingresar:
	clear
	docker exec -it --user vscode cf-dev-ia bash

run-server:
	python ./cotizacion/manage.py runserver 0.0.0.0:8000
