#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# Author: Yibin Liao
# Modified by: Dennis Gunia
# Date created: 30.03.2021
# Python Version: 3.6


from backends.BeDoH import BackEnd_DoH
from backends.BeUDP import BackEnd_UDP
from backends.BeTCP import BackEnd_TCP
from frontends.FeUDP import FrontEnd_UDP
from DNSTestThread import testServer
import time
import socket
import binascii
import Logging

backendClasses = [
    BackEnd_TCP,
    BackEnd_UDP,
    BackEnd_DoH
]

frontendClasses = [
    FrontEnd_UDP
]


class DNSProxyServer:
    def __init__(self, port, providers, config):
        self.port = int(port)
        self.providers = providers
        self.host = "127.0.0.1"
        self.config = config
        self.frontEnds = []
        self.backEnds = []
        self.masterBackend = 0
        # load backends
        try:
            backends = config["backend"].keys()
        except KeyError as exc:
            Logging.logInstance.logError("Invalid backend config at key " + exc.args[0])
            exit(102)
                
        for backend in backends:
            Logging.logInstance.logInfo("Initializing " + backend)
    
            backendObj = None
            # find matching module
            for mods in backendClasses:
                if config["backend"][backend]["type"] == mods.ident:
                    # do it 
                    backendObj = mods(config["backend"][backend],backend)
                    break
                else:
                    continue

            if backendObj == None:
                Logging.logInstance.logError("Invalid backend type " + config["backend"][backend]["type"])
                exit(104)

            self.backEnds.append(backendObj)

            # set master
            if "master" in config["backend"][backend].keys():
                if config["backend"][backend]["master"] == True:
                    self.masterBackend = len(self.backEnds) - 1


        # load frontends
        try:
            frontends = config["frontend"].keys()
        except KeyError as exc:
            Logging.logInstance.logError("Invalid frontend config at key " + exc.args[0])
            exit(102)

        for frontend in frontends:
            Logging.logInstance.logInfo("Initializing " + frontend)

            frontendObj = None
            # find matching module
            for mods in frontendClasses:
                if config["frontend"][frontend]["type"] == mods.ident:
                    # do it 
                    frontendObj = mods(config["frontend"][frontend],frontend)
                    break
                else:
                    continue

            if frontendObj == None:
                Logging.logInstance.logError("Invalid frontend type " + config["frontend"][frontend]["type"])
                exit(104)
            
            
            self.frontEnds.append(frontendObj)
            frontendObj.registerCallback(self.frontendCallback)
            frontendObj.startListener()

        while True:
            time.sleep(1)

    # callback for frontend
    def frontendCallback(self, data):

        answer = self.backEnds[self.masterBackend].send(data, self.providers.master.getIP())
        if answer:
            testServer(data,self)
            return answer
        else:
            Logging.logInstance.logError ("Request is not a DNS query. Format Error!")
            return data

##### still required for stupid analyzer

    # convert the UDP DNS query to the TCP DNS query
    def getTcpQuery(self, query):

        length = binascii.unhexlify("%04x" % len(query)) 
        return length + query

    # send a TCP DNS query to the upstream DNS server
    def sendTCP(self, DNSserverIP, query):
        server = (DNSserverIP, 53)
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(1)
        sock.connect(server)
        tcp_query = self.getTcpQuery(query)
        sock.send(tcp_query)  	
        data = sock.recv(1024)
        return data
