#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# Author: Dennis Gunia
# Date created: 12.05.2021
# Python Version: 3.6

import socket
from DNSDecodeUDP import processReq
import _thread
import json
import uuid
import sys

def testServer(req,server):
    # generate new thread
    trace_id = uuid.uuid4().hex
    _thread.start_new_thread( testThread, (req, server, trace_id,) )

def testThread(req,server, trace_id):
    
    results = []    # contains all query responses

    for provider in server.providers.providers:
        p_ip = provider.getIP()
        if len(p_ip) == 0:
            # ignore providers with no vaild IP
            continue    

        # send reuquests
        data = {}
        try:        
            TCPanswer = server.sendTCP(p_ip, req)
            if TCPanswer:
                UDPanswer = TCPanswer[2:]
                data = processReq(req,UDPanswer,p_ip)
        except socket.timeout:
            data = {
                "error": "Timeout",
                "server": p_ip
            }
        except ConnectionRefusedError:
            data = {
                "error": "Connection Refused",
                "server": p_ip
            }
        except:
            print("Unexpected error:", sys.exc_info()[0])
            data = {
                "error": "Unexpected Error",
                "server": p_ip
            }            
        results.append(data)
    

    # print (json.dumps(results, indent=4, sort_keys=True))

    # dump response to file
    filename = "debug/trace_{}.json".format(trace_id)
    with open(filename, 'w') as outfile:
        json.dump(results, fp=outfile, indent=4, sort_keys=True )