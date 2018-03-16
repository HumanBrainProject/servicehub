#!/usr/bin/env python
# -*- coding: utf-8 -*-
import asyncio
import logging
import aiodocker
from tornado.web import Application
from tornado.locks import Lock


class ServiceHubApplication(Application):
    '''Servicehub main application
    @param  dict config  The main application configuration.
    @option  dict images  The available images as: path => docker image name
    '''
    def __init__(self, config, ioloop, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.ioloop = ioloop
        loglevel = config['application'].get('logging_level', 'DEBUG')
        self.logger = logging.getLogger()
        loglevel = getattr(logging, loglevel, logging.DEBUG)
        self.logger.setLevel(loglevel)

        self.sessions = {'lock': Lock()}
        self.docker = aiodocker.Docker()
        self.images = config['images']
        self.session_lifetime = config['session'].get('lifetime', 21600)
        self.remove_container = config['session'].getboolean('remove', False)
        self.running = True

    async def shutdown(self):
        self.running = False
        self.logger.debug("Running application shutdown")
        del self.sessions['lock']
        await self._stop_containers()
        await self.docker.close()
        self.ioloop.stop()

    async def _stop_containers(self):
        self.logger.debug("Stopping containers.")
        for user, session in self.sessions.items():
            del session['lock']
            for container in session.values():
                self.logger.debug("Stopping container %s", container)
                await container.stop()
        self.logger.debug("Containers stopped.")
