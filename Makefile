#!make
ifneq ("$(wildcard .env)","")
include .env
else
endif

.DEFAULT_GOAL=up
MAKEFLAGS += --no-print-directory

# Constants
TAIL_LOGS = 50
TEST_WORKERS = auto
PYLINT_FAIL_UNDER = 8

prepare-env:
	$s cp -n .env-dist .env

up: prepare-env
	$s docker compose up --force-recreate -d

down:
	$s docker compose down

down-up: down up

up-build: down build up

build: prepare-env
	$s docker compose build

complete-build: build down-up

logs:
	$s docker logs --tail ${TAIL_LOGS} -f ${PROJECT_NAME}

bash:
	$s docker exec -it ${PROJECT_NAME} bash

sh:
	$s docker exec -it ${PROJECT_NAME} bash

uvicorn:
	$s docker exec -it ${PROJECT_NAME} uvicorn main:app --host "${FASTAPI_HOST}" --port "${FASTAPI_PORT}" --reload

restart:
	$s docker compose restart

update-dependencies:
	$s docker exec ${PROJECT_NAME} poetry update

test:
	$s docker exec ${PROJECT_NAME} unittest

ruff:
	$s docker exec ${PROJECT_NAME} ruff check .

pylint:
	$s docker exec ${PROJECT_NAME} pylint

linters: ruff pylint

black:
	$s docker exec ${PROJECT_NAME} black .

isort:
	$s docker exec ${PROJECT_NAME} isort .

code-style: isort black

IMAGES := $(shell docker images -qa)
clean-images:
	$s docker rmi $(IMAGES) --force

CONTAINERS := $(shell docker ps -qa)
remove-containers:
	$s docker rm $(CONTAINERS)