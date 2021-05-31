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

class DNSProxyServer:
    def __init__(self, pserver):
        self.pserver = pserver
        self.providers = pserver.providers
        self.host = "127.0.0.1"
        self.frontEnds = []
        self.backEnds = []
        self.masterBackend = 0

        # load backends
        try:
            backends = self.pserver.config["backend"].keys()
        except KeyError as exc:
            self.pserver.logInstance.logError("Invalid backend config at key " + exc.args[0])
            exit(102)
                
        for backend in backends:
            self.pserver.logInstance.logInfo("Initializing " + backend)
    
            backendObj = None
            # find matching module
            for mods in self.pserver.backendClasses:
                if self.pserver.config["backend"][backend]["type"] == mods.ident:
                    # do it 
                    backendObj = mods(self.pserver.config["backend"][backend],backend)
                    break
                else:
                    continue

            if backendObj == None:
                self.pserver.logInstance.logError("Invalid backend type " + self.config["backend"][backend]["type"])
                exit(104)

            self.backEnds.append(backendObj)

            # set master
            if "master" in self.pserver.config["backend"][backend].keys():
                if self.pserver.config["backend"][backend]["master"] == True:
                    self.masterBackend = len(self.backEnds) - 1


        # load frontends
        try:
            frontends = self.pserver.config["frontend"].keys()
        except KeyError as exc:
            self.pserver.logInstance.logError("Invalid frontend config at key " + exc.args[0])
            exit(102)

        for frontend in frontends:
            self.pserver.logInstance.logInfo("Initializing " + frontend)

            frontendObj = None
            # find matching module
            for mods in self.pserver.frontendClasses:
                if self.pserver.config["frontend"][frontend]["type"] == mods.ident:
                    # do it 
                    #.pserver.config["frontend"][frontend]
                    frontendObj = mods(self.pserver,frontend)
                    break
                else:
                    continue

            if frontendObj == None:
                self.pserver.logInstance.logError("Invalid frontend type " + self.pserver.config["frontend"][frontend]["type"])
                exit(104)
            
            
            self.frontEnds.append(frontendObj)
            frontendObj.registerCallback(self.frontendCallback)
            frontendObj.startListener()


    # callback for frontend
    def frontendCallback(self, data, trace_id):
        answer = self.backEnds[self.masterBackend].send(data, self.providers.master.getIP())
        if answer:
            testServer(data,self.pserver, trace_id)
            return answer
        else:
            self.pserver.logInstance.logError ("Request is not a DNS query. Format Error!")
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
