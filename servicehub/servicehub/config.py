# coding: utf-8
import configparser
import os


def get_config():
    config = configparser.ConfigParser()
    configpath = os.environ.get("SERVICEHUB_CONFIG", 'servicehub.conf')
    config.read(('/etc/servicehub.conf', configpath))
    return config
