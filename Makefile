#!make

BLUE="\033[00;94m"
GREEN="\033[00;92m"
RED="\033[00;31m"
RESTORE="\033[0m"
YELLOW="\033[00;93m"
CYAN="\e[0;96m"
GREY="\e[2;N"


clean:
	rm -rf *.pyc
	rm -rf .pytest_cache
	rm -rf .coverage

init:
	pipenv install --dev
	direnv allow
	pre-commit install

build:
	docker compose build
	docker compose up

up:
	docker compose up

down:
	docker compose down

purge:
	docker compose down --volumes --remove-orphans

rebuild: purge build

precommit:
	pre-commit run --all-files
