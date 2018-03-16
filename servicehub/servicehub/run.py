#!/usr/bin/env python
# -*- coding: utf-8 -*-
''' Run the servicehub. '''


import configparser
import os

import tornado.ioloop

from application import ServiceHubApplication
from handlers import AliveHandler, ServiceHubHandler


def _(text):
    '''Dummy gettext'''
    return text


def get_config():
    config = configparser.ConfigParser()
    configpath = os.environ.get("SERVICEHUB_CONFIG", 'servicehub.conf')
    config.read(('/etc/servicehub.conf', configpath))
    return config


class ImageMatcher(tornado.routing.HostMatches):
    """Matches requests from hosts specified by ``host_pattern`` regex."""
    def match(self, request):
        match = self.host_pattern.match(request.host)
        if match is None:
            return None
        return dict(path_kwargs=match.groupdict())


def make_app(config, ioloop, *args, **kwargs):
    images_pattern = '|'.join(config['images'].keys())
    # match any
    return ServiceHubApplication(config, ioloop, [
        (r"^/alive$", AliveHandler),
        (ImageMatcher("^(?P<image>{images_pattern})(\..*)?$".format(
            images_pattern=images_pattern)),
         ServiceHubHandler),
    ], *args, **kwargs)


def sigterm_handler(app, ioloop, *args, **kwargs):
    app.logger.info("Caught SIGTERM. Stopping service.")
    ioloop.add_callback_from_signal(app.shutdown)


if __name__ == "__main__":
    from functools import partial
    import signal
    config = get_config()
    ioloop = tornado.ioloop.IOLoop.current()
    app = make_app(config=config, ioloop=ioloop)
    app.logger.info("Starting %s", __name__)
    app.listen(8080)
    signal.signal(signal.SIGTERM, partial(sigterm_handler, app, ioloop))
    ioloop.start()
