#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# Author: Dennis Gunia
# Date created: 28.05.2021
# Python Version: 3.6
import Logging

class DNSBackEnd:
    ident = "generic"
    state = False
    
    def __init__(self, config, name):
        self.config = config
        self.name = name
        pass

    def send(self, data, ip):
        raise NotImplementedError()
