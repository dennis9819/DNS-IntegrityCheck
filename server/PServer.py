#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# Author: Dennis Gunia
# Date created: 31.05.2021
# Python Version: 3.6

from DNSProviders import DNSProviders
import yaml
from frontends.FeUDP import FrontEnd_UDP
from backends.BeUDP import BackEnd_UDP
from backends.BeDoH import BackEnd_DoH
from backends.BeTCP import BackEnd_TCP
from RedisInterface import RedisConnection
import DNSProxyServer
import DNSCliServer
import Logging
import _thread
import time
from pathlib import Path

class PServer:

    backendClasses = [
        BackEnd_TCP,
        BackEnd_UDP,
        BackEnd_DoH
    ]
    frontendClasses = [
        FrontEnd_UDP
    ]


    def __init__(self, configFile = "conf.yml"):
        self.logInstance = Logging.Logging()
        self.config = {}
        self.configFile = configFile

        try:
            with open(self.configFile, 'r') as stream:
                try:
                    self.config = yaml.safe_load(stream)
                except yaml.YAMLError as exc:
                    self.logInstance.logError("Failed to parse config")
                    print(exc)
                    exit(101)
        except FileNotFoundError as exc:
            self.logInstance.logError("Failed to open config")
            print(exc)
            exit(100)
        
        try:
            Path(self.config["varPath"] + "/log/").mkdir(parents=True, exist_ok=True)
            Path(self.config["varPath"] + "/finding/").mkdir(parents=True, exist_ok=True)
            Path(self.config["varPath"] + "/trace/").mkdir(parents=True, exist_ok=True)
        except:
            self.logInstance.logError("Failed to create directories in " + self.config["varPath"])
            exit(3)

        try:
            self.logInstance.logfile = self.config["varPath"] + "/log/pserver.log"
            self.logInstance.writeStart()
        except KeyError as exc:
            self.logInstance.logError("Invalid logfile config at key " + exc.args[0])
            exit(102)

        try:
            self.redisServer = RedisConnection(self.config["redis"]["ip"],self.config["redis"]["port"])
        except KeyError as exc:
            self.logInstance.logError("Invalid redis config at key " + exc.args[0])
            exit(102)
        pass

        self.providers = DNSProviders(self)
        self.cliServer = DNSCliServer.runCliServer(self)
        self.proxyServer = None

    def loadProvider(self,path):
        if path == '':
            try:
                path = self.config["providerFile"]
            except KeyError as exc:
                self.logInstance.logError("Invalid or missing provider config")
                exit(103)
        self.providers.loadFromFile(path)

    def writeDB(self):
        self.providers.writeStats()

    def readDB(self):
        self.providers.writeStats()

    def startServer(self):
        self.checkerThread = _thread.start_new_thread(self.__checkerThread__, ())
        self.proxyServer = DNSProxyServer.DNSProxyServer(self)

        while True:
            time.sleep(1)
 
    def __checkerThread__(self):
        while True:
            self.providers.checkInterfaces()
            time.sleep(300000) # every 5 minutes