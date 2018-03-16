# coding: utf-8
from tornado.locks import Lock
from tornado.web import HTTPError, RequestHandler
from aiodocker.exceptions import DockerError

class AliveHandler(RequestHandler):
    def get(self):
        self.write("ok\n")


class ServiceHubHandler(RequestHandler):
    def prepare(self):
        # Stop serving requests when shutdown is initiated.
        if not self.application.running:
            raise HTTPError(503, 'Service Unavailable')
        try:
            self.userid = self.request.headers['userid'].split('@', 1)[0]
        except KeyError as e:
            raise HTTPError(401,
                            'Requests need to be passed by service \
                            proxy with userid header')

    def decode_argument(self, value, name=None):
        value = super().decode_argument(value, name)
        if name == u'image':
            value = self.application.images[value]
        return value

    async def get(self, image):
        await self._get_or_create_container(image)
        self.set_header('refresh', '1; ' + self.request.uri)

    async def post(self, image):
        await self._get_or_create_container(image)
        self.redirect(self.request.uri, 307)

    async def patch(self, image):
        await self._get_or_create_container(image)
        self.redirect(self.request.uri, 307)

    async def put(self, image):
        await self._get_or_create_container(image)
        self.redirect(self.request.uri, 307)

    async def delete(self, image):
        await self._get_or_create_container(image)
        self.redirect(self.request.uri, 307)

    async def options(self, image):
        await self._get_or_create_container(image)
        self.redirect(self.request.uri, 307)

    async def _get_or_create_container(self, image):
        docker = self.application.docker
        sessions = self.application.sessions
        userid = self.userid

        name = '{userid}-{image}'.format(userid=userid, image=image)

        try:
            sessions['lock'].acquire()
            if userid not in sessions:
                sessions[userid] = {'lock': Lock()}
            session = sessions[userid]
        finally:
            sessions['lock'].release()

        try:
            # This will only allow one container to be created at a
            # time per user even in a multi-app setup. Simple form of
            # load balancing? To allow multiple applications to be
            # started simultaneously, do container level locking.
            session['lock'].acquire()

            if name in session:
                container = session[name]

            else:
                try:
                    # container exists
                    container = await docker.containers.get(name)
                except DockerError:
                    # Create new container
                    container = self._create_container(userid, image, name)

            session[name] = container

            running = container._container.get(
                "State", {}).get("Running", False)

            if not running:
                try:
                    await container.start()
                except DockerError as e:
                    self.write("Failed to start container.")
                    raise e

        finally:
            session['lock'].release()

    async def _create_container(self, userid, image, name):
        try:
            return await self.application.docker.containers.create(
                config={
                    'Image': image,
                    'Network': 'servicehub_net',
                    'Labels': {
                        'traefik.frontend.rule': 'Host:{host}; \
                        {userid_rule}; {image_rule};'.format(
                            host=self.application.request.host,
                            userid_rule='HeadersRegexp: Userid, \
                            ^[0-9]+(@.*)?$'.format(userid=userid)
                        )},
                    'HostConfig': {
                        'NetworkMode': 'servicehub_net'
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
