.PHONY: help build start stop

define HELPTEXT
Makefile usage
 Targets:
    help      this help
 	build     build the docker images
	start     start the infrastructure
	stop      stop the infrastructure
endef

export HELPTEXT
help:
	@echo "$$HELPTEXT"

build:
	docker build -t servicehub -f servicehub/Dockerfile servicehub
	docker build -t echoheaders -f sample/app/Dockerfile sample/app
	docker build -t hbpauth -f apache/Dockerfile apache

start: build stop
	docker-compose up

stop:
	docker-compose down
