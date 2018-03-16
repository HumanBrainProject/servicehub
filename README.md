# ServiceHub

Service hub provides a container infrastructure to add authentication and spawn an app per user.

The goal is to allow scientists to provide simple docker containers without managing users and sessions.

Authentication is provided by OAUTH in an Apache proxy. Docker containers are spawned for each user and destroyed after a period of inactivity.

A Traefik reverse proxy provides the routing based on a userid parameter in the header. You can see an architecture diagram [[here]] and a traffic flow schema [[here]].

## Configuring

There are two applications that need to be configured. The first is Apache which is authenticating requests. It also needs to be configured for SSL. The second is the servicehub, which needs to be provided with the Docker image for the apps, and the settings for the containers.

### Configuration files

#### Apache

Configuration file: apache/servicehub.conf
Template: apache/templates/servicehub.conf

#### Servicehub

Configuration: servicehub/servicehub.conf
Template: servicehub/templates/servicehub.conf

## Installing

    make build

## Requirements

Python >= 3.4
docker-compose
make

## Running

Start with docker compose

    make start

## Application container

For security purposes, the containerized application should not run as root!

## TODO

### Configuration wizard
 * [ ] apache
 * [ ] servicehub
 * [ ] letsencrypt

### ServiceHub

 * [ ] session monitoring from Traefik logs

### Reverse proxy
 * [ ] access logs
 * [x] Redirect non-existing route to service hub
