# coding: utf-8
import html
import pprint
import time

import tornado.ioloop
import tornado.web


class AliveHandler(tornado.web.RequestHandler):
    def get(self):
        self.write("ok\n")
        self.set_header('Content-Type', 'text/plain')


class ActivityHandler(tornado.web.RequestHandler):
    '''Really, this handler tracks inactivity.'''
    # @TODO
    # @authorized('get_activity')
    def get(self):
        '''Returns the number of seconds since the last request to the app.'''
        last_activity = self.application.last_activity
        self.write("{:d}".format(int(time.time()-last_activity)))
        self.set_header('Content-Type', 'text/plain')


class ServiceHubHandler(tornado.web.RequestHandler):
    '''Do your work here... or elsewhere.'''
    def prepare(self):
        self.application.last_activity = time.time()

    def get(self):
        '''Print headers'''
        self.write(self.fancy_headers())

    def fancy_headers(self):
        return '<html><body><pre>' + \
            html.escape(pprint.pformat(dict(self.request.headers))) + \
            '</pre></body></html>'


def make_app():
    app = tornado.web.Application([
        (r"/", ServiceHubHandler),
        # Calling /activity returns the number of seconds since the last request was made to the application.
        (r"/activity", ActivityHandler),
        # Calling /alive responds with "ok\n".
        (r"/alive", AliveHandler),
    ], autoreload=True)
    app.last_activity = time.time()
    return app


def shutdown(*args, **kwargs):
    tornado.ioloop.IOLoop.current().stop()


if __name__ == "__main__":
    import signal
    import sys
    signal.signal(signal.SIGTERM, shutdown)
    app = make_app()
    app.listen(8080)
    tornado.ioloop.IOLoop.current().start()
    sys.exit(0)
