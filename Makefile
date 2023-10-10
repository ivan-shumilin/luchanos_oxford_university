export DOCKER_DEFAULT_PLATFORM=linux/amd64

up:
	sudo docker compose -f docker-compose-local.yaml up -d

down:
	docker compose -f docker-compose-local.yaml down --remove-orphans

up_ci:
	docker compose -f docker-compose-ci.yaml up -d

up_ci_rebuild:
	docker compose -f docker-compose-ci.yaml up --build -d

down_ci:
	docker compose -f docker-compose-ci.yaml down --remove-orphans

migrate:
	alembic upgrade heads

makemigrations:
	alembic revision --autogenerate -m "comment"

