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
	docker compose -f local.yml build
	docker compose -f local.yml up

up:
	docker compose -f local.yml up

down:
	docker compose -f local.yml down

up_overwrite:
	docker compose -f local.yml -f docker compose.override.yml up

purge:
	docker compose -f local.yml down --volumes --remove-orphans

rebuild: purge build

restore_backup:
	source ./.envs/.local/mysql.env && \
	cat ./backups/backup.sql | docker exec -i prestashop_local_mysql /usr/bin/mysql -u root --password=$${MYSQL_ROOT_PASSWORD} $${MYSQL_DATABASE}

precommit:
	pre-commit run --all-files

connect_to_db:
	source ./.envs/.local/mysql.env && \
	docker exec -it prestashop_local_mysql mysql -u root --password=$${MYSQL_ROOT_PASSWORD} $${MYSQL_DATABASE}
