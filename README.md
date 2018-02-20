# ServiceHub

Service hub provides a container infrastructure to add authentication and spawn an app per user.

The goal is to allow scientists to provide simple docker containers without managing users and sessions.

Authentication is provided by OAUTH in an Apache proxy. Docker containers are spawned for each user and destroyed after a period of inactivity.


A Traefik reverse proxy provides the routing based on a userid parameter in the header.

## Installing

make install

## Requirements

Python >= 3.4
Docker deamon

## Running

Start with docker compose


    docker compose ...

## TODO

### Service hub

### Reverse proxy
 * [] Use `userid` header to route to user's container
 * [] Redirect non-existing route to service hub

### Authentication
 * [] Add Apache
 * [] Create OIDC client
 * [] Configure Apache to authenticate user
 * [] Add user id in header `userid`
