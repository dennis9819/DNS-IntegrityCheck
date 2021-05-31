#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# Author: Dennis Gunia
# Date created: 28.05.2021
# Python Version: 3.6
import datetime

import uuid

class DNSFrontEnd:
    ident = "generic"
    state = False

    def __init__(self, pserver, name):
        self.callbackFunc = None
        self.name = name
        self.pserver = pserver
        self.config = pserver.config["frontend"][name]

        # open logfile
        self.logFile = open(self.pserver.config["varPath"] + "/log/access_" + name + ".log", "a")
        pass

    def registerCallback(self, function):
        self.callbackFunc = function

    def startListener(self):
        if self.callbackFunc == None:
            raise RuntimeError("No callback assigned")
        
    def logAccess(self, ip):
        
        dateStr = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print("ip", ip)
        trace_id = uuid.uuid4().hex
        line = dateStr + " [" + self.name + "] " + ip[0] + ", " + trace_id
        self.logFile.write(line + "\n")
        self.logFile.flush()
        return trace_id
        # self.pserver.logInstance.logInfo("Initiazing Frontend type " + self.ident) 
