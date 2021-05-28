#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# Author: Dennis Gunia
# Date created: 28.05.2021
# Python Version: 3.6

from backends.Backend import DNSBackEnd
import socket
import time

class BackEnd_UDP(DNSBackEnd):
    ident = "udp"

    def __init__(self, config, name):
        super().__init__(config, name)
    
    def send(self, data, ip):
        server = (ip, 53)
        udp_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        udp_sock.sendto(data, server)
        udp_sock.settimeout(self.config["timeout"])

        recData = None
        addr = None

        for i in range(0,3):
            recData, addr = udp_sock.recvfrom(1024)
           
            if recData:
                break
            time.sleep(self.config["delay"])
            
        udp_sock.close()

        if recData == None or addr[0] != ip:
            recData = data

        return recData 


     