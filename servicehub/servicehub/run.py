#!/usr/bin/env python
# -*- coding: utf-8 -*-
''' Run the servicehub. '''
import logging
import tornado.ioloop

import config
from config import get_config
from application import ServiceHubApplication
from handlers import AliveHandler, ServiceHubHandler


def sigterm_handler(app, ioloop, *args, **kwargs):
    app.logger.info("Caught SIGTERM. Stopping service.")
    ioloop.add_callback_from_signal(app.shutdown)


if __name__ == "__main__":
    from functools import partial
    import signal
    configuration = get_config()
    loglevel = configuration['application'].get('logging_level', 'DEBUG')
    loglevel = getattr(logging, loglevel, logging.DEBUG)
    config.LOGLEVEL = loglevel
    ioloop = tornado.ioloop.IOLoop.current()
    app = ServiceHubApplication(configuration, ioloop, [
        (r"^/alive$", AliveHandler),
        (r".*", ServiceHubHandler),
    ])
    app.logger.info("Starting %s", __name__)
    http_server = app.listen(8080)
    app.http_server = http_server
    signal.signal(signal.SIGTERM, partial(sigterm_handler, app, ioloop))
    ioloop.start()
