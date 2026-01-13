.PHONY: up down logs build test e2e fmt lint db-init

up:
	docker compose up --build

down:
	docker compose down -v

logs:
	docker compose logs -f

build:
	docker compose build --no-cache

test:
	pytest -q

e2e:
	pytest -q -k auth

fmt:
	python -m black app tests

lint:
	python -m ruff check app tests

db-init:
	docker compose exec api python -m app.db.init_db
