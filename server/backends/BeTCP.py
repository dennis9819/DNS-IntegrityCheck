#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# Author: Dennis Gunia
# Date created: 28.05.2021
# Python Version: 3.6

from backends.Backend import DNSBackEnd
import socket
import Logging
import binascii

class BackEnd_TCP(DNSBackEnd):
    ident = "tcp"

    def __init__(self, config, name):
        super().__init__(config, name)
    
    def send(self, data, ip):
        TCPanswer = self.sendTCP(ip, data)
        if TCPanswer:
            UDPanswer = TCPanswer[2:]
            return UDPanswer

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
