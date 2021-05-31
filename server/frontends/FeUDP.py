#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# Author: Dennis Gunia
# Date created: 28.05.2021
# Python Version: 3.6

from frontends.Frontend import DNSFrontEnd

import socket
import Logging
import _thread


class FrontEnd_UDP(DNSFrontEnd):
    ident = "udp"

    def __init__(self, config, name):
        super().__init__(config, name)
    
    def startListener(self):
        super().startListener()
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        try:
            self.sock.bind((self.config["host"], self.config["port"]))
        except KeyError as exc:
            self.pserver.logInstance.logError("Invalid frontend config at key " + exc.args[0])
            exit(102)

        self.listenIdent = _thread.start_new_thread(self.__listen__, ())
        
    def logAccess(self, ip):
        return super().logAccess(ip)

    def __listen__(self):
        self.pserver.logInstance.logInfo("Started listener thread for frontend " \
            + self.name + " (" \
            + self.ident  +  ") @ " \
            + hex(_thread.get_ident())) 
        
        try:
            while True:
                data, addr = self.sock.recvfrom(1024)
                trace_id = self.logAccess(addr)
                _thread.start_new_thread(self.__connection__, (data, addr, trace_id))
        except:
            self.pserver.logInstance.logError("Error occured in listener thread for frontend " \
                + self.name + " (" \
                + self.ident  +  ") @ " \
                + hex(_thread.get_ident())) 

            _thread.interrupt_main()

    def __connection__(self,data,addr, trace_id):
        returnData = self.callbackFunc(data, trace_id)
        # reply
        self.sock.sendto(returnData, addr)

    