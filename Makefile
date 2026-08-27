.PHONY: help install test seed run-backend run-frontend docker-up docker-down clean

help:
	@echo "FreshCart Grocery & Logistics Platform - Commands"
	@echo "  make install        Install Python backend & frontend dependencies"
	@echo "  make test           Run all backend pytest suites"
	@echo "  make seed           Seed the database with complete master grocery catalog"
	@echo "  make run-backend    Start FastAPI backend server on port 8000"
	@echo "  make run-frontend   Start Next.js frontend dev server on port 3000"
	@echo "  make docker-up      Launch full production stack in Docker Compose"
	@echo "  make docker-down    Stop Docker Compose services"
	@echo "  make clean          Clean temporary files and caches"

install:
	pip install -r backend/requirements.txt
	cd frontend && npm install

test:
	pytest -v backend/tests

seed:
	python backend/scripts/seed_data.py

run-backend:
	uvicorn backend.app.main:app --reload --port 8000

run-frontend:
	cd frontend && npm run dev

docker-up:
	docker-compose up --build -d

docker-down:
	docker-compose down

clean:
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type d -name ".pytest_cache" -exec rm -rf {} +
