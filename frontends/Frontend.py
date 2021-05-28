#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# Author: Dennis Gunia
# Date created: 28.05.2021
# Python Version: 3.6

import Logging

class DNSFrontEnd:
    ident = "generic"
    state = False

    def __init__(self, config, name):
        self.callbackFunc = None
        self.config = config
        self.name = name
        pass

    def registerCallback(self, function):
        self.callbackFunc = function

    def startListener(self):
        if self.callbackFunc == None:
            raise RuntimeError("No callback assigned")
        
        # Logging.logInstance.logInfo("Initiazing Frontend type " + self.ident) 
