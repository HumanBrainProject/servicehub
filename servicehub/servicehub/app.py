# coding: utf-8
import time


import docker
import tornado.ioloop
import tornado.web

# Number of seconds of inactivity before killing the container
SESSION_LENGTH = 15*60
# Number of seconds before assuming we failed to start the container
STARTUP_MAX_TIME = 60
NETWORK = 'servicehub_net'

CREATED = 'created'
DEAD = 'dead'
EXITED = 'exited'
NOT_STARTED = 'not_started'
PAUSED = 'paused'
RESTARTING = 'restarting'
RUNNING = 'running'

def _(text):
    '''Dummy gettext'''
    return text


class AliveHandler(tornado.web.RequestHandler):
    def get(self):
        self.write("ok\n")


class ContainerizedApp:

    def __init__(self, request):
        self.client = docker.from_env()
        self.request = request

    def get_container_id(self):
        return '1'

    def get_route_rule(self):
        pass

    def get_image_name(self):
        pass

    def get_host(self):
        pass

    def get_container_name(self):
        return '{image}-{id}'.format(
            image=self.get_image_name(),
            id=self.get_container_id()
        )

    def is_concerned(self):
        return self.request.headers['Host'] == self.get_host()

    def start(self):
        return self.client.containers.run(
            self.get_image_name(),
            detach=True,
            remove=True,
            name=self.get_container_name(),
            network=NETWORK,
            labels={
                'traefik.frontend.rule': 'Host:{host}; {rule}'.format(
                    host=self.get_host(),
                    rule=self.get_route_rule()
                )
            }
        )

    def get_header(self, name):
        return self.request.headers[name]

    def remove(self):
        self.get_container().remove()

    def unpause(self):
        self.get_container().unpause()

    def get_container(self):
        return self.client.containers.get(self.get_container_name())

    def get_state(self):
        try:
            return self.get_container().status
        except docker.errors.NotFound:
            return NOT_STARTED

class EchoHeadersApp(ContainerizedApp):
    def get_host(self):
        return 'echo.localhost'

    def get_container_id(self):
        return self.get_header('Oidc_claim_sub')

    def get_route_rule(self):
        return 'Headers: Oidc_claim_sub, {userid};'.format(
            userid=self.get_header('Oidc_claim_sub')
        )

    def get_image_name(self):
        return 'echoheaders'


class ServiceHubHandler(tornado.web.RequestHandler):
    # @tornado.web.asynchronous
    apps = [EchoHeadersApp]
    def get(self):
        containerized_app = self.get_concerned_app()

        if containerized_app is None:
            self.write("No app configured for this route")
            return

        state = containerized_app.get_state()

        if state in [NOT_STARTED, CREATED, EXITED]:
            self.write("You have no container, we will spawn one")
            containerized_app.start()

        if state == DEAD:
            self.write("Your container failed stopping, we will spawn a new one")
            containerized_app.remove()

        if state == PAUSED:
            self.write("Your container is paused, we will unpause it")
            containerized_app.unpause()

        if state == RESTARTING:
            self.write("Your container is restarting")

        if state == RUNNING:
            self.write("Error: Your container is running, what are you doing here?")

        self.set_header('refresh', '3; ' + self.request.uri)

    def get_concerned_app(self):
        for App in self.apps:
            containerized_app = App(self.request)
            if containerized_app.is_concerned():
                return containerized_app
        return None

class ServiceHubApplication(tornado.web.Application):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # TODO: I think this is threadsafe assuming tornado doesn't
        # pause thread execution at wrong moment. otherwise, use
        # something else then dictionary.
        self.user_sessions = {}


def make_app():
    return ServiceHubApplication([
        (r"/", ServiceHubHandler),
        (r"/alive", AliveHandler),
    ], autoreload=True)


# @TODO initialize and clean docker images


if __name__ == "__main__":
    app = make_app()
    app.listen(8080)
    tornado.ioloop.IOLoop.current().start()
