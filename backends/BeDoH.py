#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# Author: Dennis Gunia
# Date created: 28.05.2021
# Python Version: 3.6

from os import name
from DNSPacket import DNSPacket
from backends.Backend import DNSBackEnd
import base64
import requests

# DoH implementation according to rfc8484 - DNS Queries over HTTPS (DoH)
class BackEnd_DoH(DNSBackEnd):
    ident = "doh"

    def __init__(self, config, name):
        super().__init__(config, name)
    
    def send(self, data, ip):
        # dns over https
        query = (base64.b64encode(data)).decode("utf-8").replace("=","")
        string = "https://{}/{}?dns={}".format(ip,self.config["url"],query) 
        r =requests.get(string)
        recData = r.content
   
        if r.status_code == 200 and r.headers['Content-Type'] == 'application/dns-message':
            return recData
        else:
            return data