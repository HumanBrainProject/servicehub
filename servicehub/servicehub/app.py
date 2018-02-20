# coding: utf-8

import docker
import tornado.ioloop
import tornado.web

SESSION_LENGTH = 15*60


class ServiceHubHandler(tornado.web.RequestHandler):
    def initialize(self, sessions):
        self.sessions = sessions

    def get(self):
        userid = self.request.headers['userid']
        if userid in self.sessions:
            self.write("session already exists\n")
            return
        # @todo main queue for creation to avoid multiple simultaneous logins
        client = docker.from_env()
        self.sessions[userid] = client.containers.run("emilevauge/whoami", detach=True, remove=True)
        self.write(str(self.sessions[userid]) +"\n")
        self.set_header('refresh', '5; ' + self.request.url)


sessions = {}


def make_app():
    return tornado.web.Application([
        (r"/", ServiceHubHandler, {'sessions': {}}),
    ])


# @TODO initialize and clean docker images


if __name__ == "__main__":
    app = make_app()
    app.listen(8889)
    tornado.ioloop.IOLoop.current().start()
