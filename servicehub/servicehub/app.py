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
CONTAINER_IMAGE = "emilevauge/whoami"
NETWORK = 'servicehub_net'

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

        try:
            container = sessions[userid]
        except KeyError:
            self.start_container(userid)
            self.write(str(sessions[userid]) + "\n")
            self.set_header('refresh', '1; ' + self.request.uri)
            return

        if container is None:
            self.set_header('refresh', '5; ' + self.request.uri)
            self.write(_("We are launching your application, please be patient"))
        elif isinstance(container, int):
            if time.time() - container > STARTUP_MAX_TIME:
                # @TODO
                self.write(_("session failed to start\n"))
            else:
                self.set_header('refresh', '5; ' + self.request.uri)
                self.write(_("We are launching your application, please be patient"))
        elif container.status in ('running', 'created'):
            self.write(_("Error: Your container is running, what are you doing here?"))
            # @TODO what to do?
        elif container.status == 'exited':
            # Don't do anything, we'll create a new container
            self.write(_("Your container had exited, started a new on.?"))
            del sessions[userid]
            self.set_header('refresh', '1; ' + self.request.uri)
        else:
            # @TODO what?
            print("error: ")
            print(container)
            print(container.status)
        return

    def start_container(self, userid):
        sessions = self.application.user_sessions
        client = docker.from_env()
        sessions[userid] = None
        sessions[userid] = time.time()
        sessions[userid] = client.containers.run(
            CONTAINER_IMAGE,
            detach=True,
            remove=True,
            name='app-{userid}'.format(userid=userid),
            network=NETWORK,
            labels={
                'traefik.frontend.rule': 'Host:{host}; Headers: userid, {userid};'.format(host='hub.localhost', userid=userid)
            }
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
