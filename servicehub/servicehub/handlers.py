# coding: utf-8
import logging
import uuid

from tornado.web import HTTPError, RequestHandler
from aiodocker.exceptions import DockerError

import config


class AliveHandler(RequestHandler):
    def get(self):
        self.write("ok\n")


request_formatter = logging.Formatter(
    '%(asctime)s - rid: %(request_id)s - uid: %(userid)s \
    - %(levelname)s - %(message)s')


class ServiceHubHandler(RequestHandler):
    def log_filter(self, record):
        record.userid = self.userid
        record.request_id = self.request_id
        return True

    def prepare(self):
        self.logger = logging.Logger('servicehub.handlers')
        self.logger.setLevel(config.LOGLEVEL)
        ch = logging.StreamHandler()
        ch.setFormatter(request_formatter)
        self.logger.addHandler(ch)
        self.logger.addFilter(self.log_filter)
        self.request_id = uuid.uuid1().hex
        try:
            self.userid = self.request.headers['userid'].split('@', 1)[0]
        except KeyError as e:
            raise HTTPError(401,
                            'Requests need to be passed by service \
                            proxy with userid header')

    async def _handle(self):
        image = self.application.image
        label = self.application.image_label
        remove = self.application.image_remove
        self.logger.debug("Request for user %s", self.userid)
        self.write("I am working hard to create your application. \
            Give me a few moments.")
        await self._get_or_create_container(image, label, remove)
        self.redirect(self.request.uri, 307)

    get = post = patch = put = delete = options = _handle

    async def _get_or_create_container(self, image, label, remove):
        userid = self.userid
        name = '{userid}-{image}'.format(userid=userid, image=image)

        with self.application.session_manager.get(name) as session:
            if 'container' not in session:
                session['container'] = await self._docker_find_container(
                    userid, image, name, label, remove)

            container = session['container']

            running = container._container.get(
                "State", {}).get("Running", False)

            if not running:
                self.logger.debug("Starting container.")
                try:
                    await container.start()
                except DockerError as e:
                    self.logger.warn("Failed to start container.")
                    raise e

    async def _docker_find_container(self, userid, image, name, label, remove):
        docker = self.application.docker
        try:
            # container exists
            container = await docker.containers.get(name)
            self.logger.debug('Found container for %s.', self.userid)
            return container
        except DockerError:
            # Create new container
            self.logger.debug('Creating container for %s.', self.userid)
            return await self._create_container(
                userid, image, name, label, remove)

    async def _create_container(self, userid, image, name, label, remove):
        try:
            return await self.application.docker.containers.create(
                config={
                    'Image': image,
                    'Label': label,
                    'Network': 'servicehub_net',
                    'Labels': {
                        'traefik.frontend.rule': 'Host:{host}; \
                        {userid_rule};'.format(
                            host=self.request.host,
                            userid_rule='HeadersRegexp: Userid, \
                            ^[0-9]+(@.*)?$'.format(userid=userid)
                        )},
                    'HostConfig': {
                        'NetworkMode': 'servicehub_net',
                        'AutoRemove': remove,
                    },
                    'AttachStdin': False,
                    'AttachStdout': False,
                    'AttachStderr': False,
                    'Tty': False,
                    'OpenStdin': False,
                },
                name=name
            )
        except DockerError as e:
            self.logger.warn("Failed to create container for %s.", userid)
            raise e
