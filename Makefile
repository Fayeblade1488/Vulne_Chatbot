.PHONY: setup run test benchmark clean docker-build docker-run help

# Default target
help:
	@echo "Available targets:"
	@echo "  setup        - Setup development environment"
	@echo "  run          - Run the vulnerable chatbot"
	@echo "  test         - Run tests"
	@echo "  benchmark    - Run benchmarks"
	@echo "  clean        - Clean temporary files"
	@echo "  docker-build - Build Docker image"
	@echo "  docker-run   - Run Docker container"

# Setup development environment
setup:
	python3 -m venv venv
	./venv/bin/pip install --upgrade pip
	./venv/bin/pip install -r requirements.txt
	@if [ -f requirements-dev.txt ]; then ./venv/bin/pip install -r requirements-dev.txt; fi
	./venv/bin/pip install -e benchmarking/
	@echo "Setup complete! Activate venv with: source venv/bin/activate"

# Run the vulnerable chatbot
run:
	@if [ ! -d venv ]; then make setup; fi
	./venv/bin/python app/vulne_chat.py

# Run tests
test:
	@if [ ! -d venv ]; then make setup; fi
	./venv/bin/pytest tests/ -v

# Run benchmarks
benchmark:
	@if [ ! -d venv ]; then make setup; fi
	./venv/bin/python benchmarking/vulne_bench/runners/run_all.py

# Clean temporary files
clean:
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -delete
	find . -name ".DS_Store" -delete
	rm -rf .pytest_cache/
	rm -rf data/results/*
	rm -rf master_results_*
	rm -rf benchmark_reports_*
	rm -f *.log
	rm -f guardrails_state.json

# Docker operations
docker-build:
	docker build -t vulne-chatbot .

docker-run:
	@if [ ! -f .env.real ]; then echo "Error: .env.real not found. Copy .env.example to .env.real and configure it."; exit 1; fi
	docker run -p 7000:7000 --env-file .env.real vulne-chatbot

# Development server with auto-reload
dev:
	@if [ ! -d venv ]; then make setup; fi
	./venv/bin/python app/vulne_chat.py --debug
