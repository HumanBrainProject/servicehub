# coding: utf-8
from tornado.web import HTTPError, RequestHandler
from aiodocker.exceptions import DockerError


class AliveHandler(RequestHandler):
    def get(self):
        self.write("ok\n")


class ServiceHubHandler(RequestHandler):
    def prepare(self):
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
                try:
                    await container.start()
                except DockerError as e:
                    self.write("Failed to start container.")
                    raise e

    async def _docker_find_container(self, userid, image, name, label, remove):
        docker = self.application.docker
        try:
            # container exists
            return await docker.containers.get(name)
        except DockerError:
            # Create new container
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
            self.write("Failed to create container.")
            raise e
