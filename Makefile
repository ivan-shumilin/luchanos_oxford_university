export DOCKER_DEFAULT_PLATFORM=linux/amd64

up:
	sudo docker compose -f docker-compose-local.yaml up -d

down:
	sudo docker compose -f docker-compose-local.yaml down --remove-orphans

up_ci:
	sudo docker compose -f docker-compose-ci.yaml up -d

up_ci_rebuild:
	sudo docker compose -f docker-compose-ci.yaml up --build -d

down_ci:
	docker compose -f docker-compose-ci.yaml down --remove-orphans
