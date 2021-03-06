#!/usr/bin/python2

import asyncore
import logging
import sys
from ConfigParser import ConfigParser

try:
    import construct
    del construct
except ImportError:
    import os
    sys.path.insert(0, os.path.join(os.getcwd(), "external"))

import net
import net.mapserv as mapserv
import plugins
from utils import extends
from itemdb import load_itemdb
from loggers import debuglog
from logicmanager import logic_manager


@extends('smsg_player_warp')
def player_warp(data):
    mapserv.cmsg_map_loaded()


@extends('smsg_map_login_success')
def map_login_success(data):
    mapserv.cmsg_map_loaded()


if __name__ == '__main__':
    rootLogger = logging.getLogger('')
    rootLogger.addHandler(logging.NullHandler())

    dbgh = logging.StreamHandler(sys.stdout)
    dbgh.setFormatter(logging.Formatter("[%(asctime)s] %(message)s",
                                        datefmt="%Y-%m-%d %H:%M:%S"))
    debuglog.addHandler(dbgh)
    debuglog.setLevel(logging.INFO)

    shoplog = logging.getLogger('ManaChat.Shop')
    shoplog.setLevel(logging.INFO)
    shoplog.addHandler(dbgh)

    config = ConfigParser()
    config.read('manachat.ini')

    load_itemdb('itemdb.txt')

    plugins.load_plugins(config)

    net.login(host=config.get('Server', 'host'),
              port=config.getint('Server', 'port'),
              username=config.get('Player', 'username'),
              password=config.get('Player', 'password'),
              charname=config.get('Player', 'charname'))

    while True:
        asyncore.loop(timeout=0.2, count=5)
        logic_manager.tick()
