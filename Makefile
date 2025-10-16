.PHONY: help install setup run migrate test clean docker-up docker-down

help:
	@echo "Available commands:"
	@echo "  make install      - Install dependencies"
	@echo "  make setup        - Setup environment and database"
	@echo "  make run          - Run development server"
	@echo "  make migrate      - Run database migrations"
	@echo "  make seed         - Seed database with sample data"
	@echo "  make test         - Run tests"
	@echo "  make clean        - Clean up temporary files"
	@echo "  make docker-up    - Start Docker containers"
	@echo "  make docker-down  - Stop Docker containers"

install:
	pip install -r requirements.txt

setup:
	cp .env.example .env
	python scripts/init_db.py

run:
	python run.py

migrate:
	flask db migrate
	flask db upgrade

seed:
	python scripts/seed_data.py

test:
	python -m pytest

clean:
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
	find . -type f -name "*.log" -delete

docker-up:
	docker-compose up -d

docker-down:
	docker-compose down

docker-logs:
	docker-compose logs -f backend

