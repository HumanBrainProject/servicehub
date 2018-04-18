# ServiceHub

Service hub provides a container infrastructure to add authentication and spawn an app per user.

The goal is to allow scientists to provide simple docker containers without managing users and sessions.

Authentication is provided by OAUTH in an Apache proxy. Docker containers are spawned for each user and destroyed after a period of inactivity.

A Traefik reverse proxy provides the routing based on a userid parameter in the header. You can see an architecture diagram [[here]] and a traffic flow schema [[here]].

## Configuring

There are two applications that need to be configured. The first is Apache which is authenticating requests. It needs OpenID tokens to connect to our OpenID provider, and also needs to be configured for SSL. The second is the servicehub, which needs to be provided with the Docker image for the apps, and the settings for the containers.

### OIDC Client registration

You application will need to be registered with the OpenID Connect server. You can register [here](https://collab.humanbrainproject.eu/#/collab/54/nav/1051) using the server flow. You must be an HBP member to access this service.

### Configuration files

- _docker-compose.yaml_:
  Get an SSL certificate for your domain. You can find steps for setting it up with Letsencrypt [here](https://letsencrypt.org/getting-started/).
  Once you have SSL certificates, update the mapping in `docker-compose.yaml`'s 'services/volumes' to point to the certificate directory. For Debian based distros, this will usually be `/etc/letsencrypt/live` if you use letsencrypt's certbot to obtain the certificates.
- _apache/servicehub.conf_:
  Copy apache/servicehub.conf.example to apache/servicehub.conf and configure the OIDC parameters.
  + ServerName: your domain name
  + OIDCClientID: the client ID you obtained from the collab when creating a client.
  + OIDCClientSecret: the secret you obtained from the collab when creating a client.
  + OIDCRedirectUri: http(s)://my-domain.org/redirect_uri
  + OIDCCryptoPassphrase: a secret random passphrase
  + @TODO SSL CONFIG
- _servicehub/servicehub.conf_:
  Copy servicehub/servicehub.conf.example to servicehub/servicehub.conf
  Update the image name and optionnaly label to use your application's image.
  NOTE: The session lifetime is not implemented yet.

## Installing

    make build

## Requirements

Python >= 3.4
docker-compose
make

## Running

Start with docker compose

    make start

You should now be able to access the app at the domain you have set in the Apache vhost (assuming that you have set the DNS). You should be redirected to the Human Brain Login page, which will ask you whether you authorize it to give you access to the scopes you have requested during the client registration. Once you sign in and accept, your application should load. If your home page is /hello, browse to http(s)://my-domain.org/hello.

## Application

For security purposes, the containerized application should not run as root!

## Authentication and user ACLs

## Connecting to services

### Configuration wizard
 * [ ] apache
 * [ ] servicehub
 * [ ] letsencrypt

### ServiceHub

 * [ ] session monitoring from Traefik logs

### Reverse proxy
 * [ ] access logs
 * [x] Redirect non-existing route to service hub
