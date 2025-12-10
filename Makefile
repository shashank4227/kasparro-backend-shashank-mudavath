.PHONY: up down test clean

up:
	docker-compose up --build -d

down:
	docker-compose down

test:
	docker-compose run --rm app python -m pytest

clean:
	docker-compose down -v
	rm -rf __pycache__ .pytest_cache
