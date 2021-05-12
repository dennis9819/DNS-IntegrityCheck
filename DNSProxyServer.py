#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# Author: Yibin Liao
# Modified by: Dennis Gunia
# Date created: 30.03.2021
# Python Version: 3.6


from DNSTestThread import testServer
from DNSDecodeUDP import processReq
import socket
import sys
import _thread
import traceback
import binascii

class DNSProxyServer:
    def __init__(self, port, providers):
        self.port = int(port)
        self.providers = providers
        self.host = "127.0.0.1"
        print("[INFO ]   Opening on {}:{}".format(self.host,self.port)) 
        try:
            # setup a UDP server to get the UDP DNS request
            sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            sock.bind((self.host, self.port))
            while True:
                data, addr = sock.recvfrom(1024)
                _thread.start_new_thread(self.handler, (data, addr, sock, providers.master.getIP()))
        except OSError as err:
            print("[ERROR]   {}".format(err)) 
        except TypeError as err:
            print("[ERROR]   {}".format(err)) 
        except:
            print("Unexpected error:", sys.exc_info()[0])
            traceback.print_exc()
            sock.close()

    # a new thread to handle the UPD DNS request to TCP DNS request
    def handler(self, data, addr, socket, DNSserverIP):
        TCPanswer = self.sendTCP(DNSserverIP, data)
        if TCPanswer:
            UDPanswer = TCPanswer[2:]
            socket.sendto(UDPanswer, addr)
            testServer(data,self)
        else:
            print ("Request is not a DNS query. Format Error!")

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
