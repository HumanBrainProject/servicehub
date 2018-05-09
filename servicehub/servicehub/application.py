#!/usr/bin/env python
# -*- coding: utf-8 -*-
import logging
import aiodocker
from tornado.web import Application
from session_manager import SessionManager
import config


class ServiceHubApplication(Application):
    '''Servicehub main application
    @param  dict config  The main application configuration.
    @option  dict images  The available images as: path => docker image name
    '''
    def __init__(self, config_, ioloop, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.ioloop = ioloop
        self.logger = logging.getLogger('servicehub')
        self.logger.setLevel(config.LOGLEVEL)

        self.session_manager = SessionManager()
        self.docker = aiodocker.Docker()
        image_config = config_['image']
        self.image = image_config.get('name')
        self.image_label = image_config.get('label', 'latest')
        self.image_remove = image_config.getboolean('remove', False)
        self.session_lifetime = config_['session'].get('lifetime', 21600)
        self.remove_container = config_['session'].getboolean('remove', False)

    async def shutdown(self):
        self.logger.debug("Running application shutdown")
        self.http_server.stop()
        await self._stop_containers()
        await self.docker.close()
        self.ioloop.stop()

    async def _stop_containers(self):
        self.logger.debug("Stopping containers.")
        for user, session in self.session_manager.items():
            container = session['container']
            self.logger.debug("Stopping container %s", container)
            await container.stop()
        self.logger.debug("Containers stopped.")
