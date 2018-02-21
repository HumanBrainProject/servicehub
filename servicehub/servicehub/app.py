# coding: utf-8
import time


import docker
import tornado.ioloop
import tornado.web

# Number of seconds of inactivity before killing the container
SESSION_LENGTH = 15*60
# Number of seconds before assuming we failed to start the container
STARTUP_MAX_TIME = 60
# Container to run
CONTAINER_IMAGE = "app-to-run"
NETWORK = 'servicehub_net'

NOT_STARTED = 'state.not_started'
STARTING_FAILED = 'state.starting_failed'
STARTING = 'state.starting'
RUNNING = 'state.running'
EXITED = 'state.exited'
DEFAULT = 'state.default'

def _(text):
    '''Dummy gettext'''
    return text


class AliveHandler(tornado.web.RequestHandler):
    def get(self):
        self.write("ok\n")


class ServiceHubHandler(tornado.web.RequestHandler):
    # @tornado.web.asynchronous
    def get(self):
        userid = self.request.headers['userid']
        sessions = self.application.user_sessions

        state = self.get_state(sessions, userid)

        if state == NOT_STARTED:
            self.start_container(userid)
            self.write(str(sessions[userid]) + "\n")
            self.set_header('refresh', '1; ' + self.request.uri)
            return

        if state == STARTING_FAILED:
            self.write(_("session failed to start\n"))
            return

        if state == STARTING:
            self.set_header('refresh', '5; ' + self.request.uri)
            self.write(_("We are launching your application, please be patient"))
            return

        if state == RUNNING:
            self.write(_("Error: Your container is running, what are you doing here?"))
            # @TODO what to do?
            return

        if state == EXITED:
            # Don't do anything, we'll create a new container
            self.write(_("Your container had exited, started a new on.?"))
            del sessions[userid]
            self.set_header('refresh', '1; ' + self.request.uri)
            return

        if state == DEFAULT:
            # @TODO what?
            print("error: ")
            print(container)
            print(container.status)
            return

    def get_state(self, sessions, userid):
        try:
            container = sessions[userid]
        except KeyError:
            return NOT_STARTED

        if isinstance(container, int):
            if time.time() - container > STARTUP_MAX_TIME:
                return STARTING_FAILED

            return STARTING

        if container.status in ('running', 'created'):
            return RUNNING

        if container.status == 'exited':
            return EXITED

        return DEFAULT

    def start_container(self, userid):
        sessions = self.application.user_sessions
        client = docker.from_env()
        sessions[userid] = int(time.time())
        sessions[userid] = client.containers.run(
            CONTAINER_IMAGE,
            detach=True,
            remove=True,
            name='app-{userid}'.format(userid=userid.split('@')[0]),
            network=NETWORK,
            labels={
                'traefik.frontend.rule': 'Host:{host}; Headers: userid, {userid};'.format(host='hub.localhost', userid=userid)
            },
            environment={'USER': userid}
        )


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
