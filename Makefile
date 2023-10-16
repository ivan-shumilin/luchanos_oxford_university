export DOCKER_DEFAULT_PLATFORM=linux/amd64

DATE := $(shell date +%Y-%m-%d__%H-%M)

up:
	sudo docker compose -f docker-compose-local.yaml up -d

down:
	sudo docker compose -f docker-compose-local.yaml down --remove-orphans

dump:
	pg_dump -U postgres -h 0.0.0.0 -Fc postgres > ./$(DATE)__backup.sql

restore:
	pg_restore -U postgres -h 0.0.0.0 -d postgres -c backup.sql

dump_ci:
	pg_dump -U postgres -h 37.140.195.68 -Fc postgres > ./dump/$(DATE)__backup.sql

restore_ci:
	pg_restore -U postgres -h 37.140.195.68 -d postgres -c backup.sql

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