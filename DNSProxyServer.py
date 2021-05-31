#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# Author: Yibin Liao
# Modified by: Dennis Gunia
# Date created: 30.03.2021
# Python Version: 3.6


from DNSTestThread import testServer
import time
import socket
import binascii
import Logging




class DNSProxyServer:
    def __init__(self, port, providers, interfaces):
        self.port = int(port)
        self.providers = providers
        self.host = "127.0.0.1"
        self.frontEnds = []
        self.backEnds = []
        self.masterBackend = 0
        self.backendClasses, self.frontendClasses, self.config = interfaces
        # load backends
        try:
            backends = self.config["backend"].keys()
        except KeyError as exc:
            Logging.logInstance.logError("Invalid backend config at key " + exc.args[0])
            exit(102)
                
        for backend in backends:
            Logging.logInstance.logInfo("Initializing " + backend)
    
            backendObj = None
            # find matching module
            for mods in self.backendClasses:
                if self.config["backend"][backend]["type"] == mods.ident:
                    # do it 
                    backendObj = mods(self.config["backend"][backend],backend)
                    break
                else:
                    continue

            if backendObj == None:
                Logging.logInstance.logError("Invalid backend type " + self.config["backend"][backend]["type"])
                exit(104)

            self.backEnds.append(backendObj)

            # set master
            if "master" in self.config["backend"][backend].keys():
                if self.config["backend"][backend]["master"] == True:
                    self.masterBackend = len(self.backEnds) - 1


        # load frontends
        try:
            frontends = self.config["frontend"].keys()
        except KeyError as exc:
            Logging.logInstance.logError("Invalid frontend config at key " + exc.args[0])
            exit(102)

        for frontend in frontends:
            Logging.logInstance.logInfo("Initializing " + frontend)

            frontendObj = None
            # find matching module
            for mods in self.frontendClasses:
                if self.config["frontend"][frontend]["type"] == mods.ident:
                    # do it 
                    frontendObj = mods(self.config["frontend"][frontend],frontend)
                    break
                else:
                    continue

            if frontendObj == None:
                Logging.logInstance.logError("Invalid frontend type " + self.config["frontend"][frontend]["type"])
                exit(104)
            
            
            self.frontEnds.append(frontendObj)
            frontendObj.registerCallback(self.frontendCallback)
            frontendObj.startListener()

        while True:
            time.sleep(1)

    # callback for frontend
    def frontendCallback(self, data):
        print(data)
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
