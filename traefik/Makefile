APP_DOCKERFILE := Dockerfile.app
APP_IMAGE := app-to-run
HUB_DOCKERFILE := Dockerfile.hub
HUB_IMAGE := hbp-hub
TRAEFIK_NETWORK := traefik_net
HOST := hub.localhost

.PHONY: help build up down prune run stop

define HELPTEXT
Makefile usage
 Targets:
 	build        build the image of the demo app and the hub
	down         stop the infrastructure
 	help         this help
	run  USER=me run  the app for the given user
	stop USER=me stop the app for the given user
	up           spawn the infrastructure
endef

export HELPTEXT
help:
	@echo "$$HELPTEXT"

build:
	docker build -t $(APP_IMAGE) -f $(APP_DOCKERFILE) .
	docker build -t $(HUB_IMAGE) -f $(HUB_DOCKERFILE) .

up: build
	docker-compose up -d

down:
	docker-compose down

run: up
	docker create \
	  --name app-$(USER) \
	  --label traefik.frontend.rule="Host:$(HOST); Headers: userid, $(USER);" \
	  --network $(TRAEFIK_NETWORK) \
	  -e USER=$(USER) \
	  $(APP_IMAGE)
	docker start app-$(USER)

stop:
	docker stop app-$(USER)
	docker rm app-$(USER)
