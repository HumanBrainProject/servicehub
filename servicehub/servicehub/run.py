#!/usr/bin/env python
# -*- coding: utf-8 -*-
''' Run the servicehub. '''


import configparser
import os

import tornado.ioloop

from application import ServiceHubApplication
from handlers import AliveHandler, ServiceHubHandler


def get_config():
    config = configparser.ConfigParser()
    configpath = os.environ.get("SERVICEHUB_CONFIG", 'servicehub.conf')
    config.read(('/etc/servicehub.conf', configpath))
    return config


def sigterm_handler(app, ioloop, *args, **kwargs):
    app.logger.info("Caught SIGTERM. Stopping service.")
    ioloop.add_callback_from_signal(app.shutdown)


if __name__ == "__main__":
    from functools import partial
    import signal
    config = get_config()
    ioloop = tornado.ioloop.IOLoop.current()
    app = ServiceHubApplication(config, ioloop, [
        (r"^/alive$", AliveHandler),
        (r".*", ServiceHubHandler),
    ])
    app.logger.info("Starting %s", __name__)
    http_server = app.listen(8080)
    app.http_server = http_server
    signal.signal(signal.SIGTERM, partial(sigterm_handler, app, ioloop))
    ioloop.start()
