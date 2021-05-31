#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# Author: Dennis Gunia
# Date created: 26.05.2021
# Python Version: 3.6

from multiprocessing.connection import Listener
import _thread
from os import name


SERVER_VERSION='0.0.1'
SERVER_VERSION_NUM='1'
def runCliServer(pserver):
    # generate new thread
    _thread.start_new_thread( runCliServerThread, (pserver, ) )

def runCliServerThread(pserver):
    pserver.logInstance.logInfo("Started CLI-Server Thread")
    address = ('localhost', 6000)     # family is deduced to be 'AF_INET'
    while True:
        listener = Listener(address, authkey=b'secret password')
        try:
            conn = listener.accept()
            while True:
                msg = conn.recv()
                # do something with msg
                if msg == 'cmd:exit':
                    break
                elif msg == 'getver':
                    conn.send([SERVER_VERSION,SERVER_VERSION_NUM])
                elif msg[0:4] == 'cmd:':
                    cmdGlobal(conn,msg,pserver)
                    conn.send([9999,''])
                else:
                    conn.send([1,'Unknown operation'])
            listener.close()
        except:
            listener.close()
            pass

def cmdGlobal(conn,cmd, pserver):
    helpMsg = """Modules:
    help
    providers
    status"""
    
    segments = cmd[4:].split(' ')
    # print("got:" , segments[0])
    if segments[0] == 'ping':
        conn.send([0,"pong"])
    elif segments[0] == 'providers' or segments[0] == 'provider':
        cmdModProviders(conn,segments[1:],pserver.providers)
    elif segments[0] == 'status':
        cmdModStatus(conn,segments[1:],pserver.providers)
    elif segments[0] == 'help':
        conn.send([0,helpMsg]) 
    else:
        conn.send([1,"Module not found"])
        conn.send([0,helpMsg])

def cmdModProviders(conn,segments, providers):
    
    helpMsg = """Operations:
    get [:id]
    get
    list
    save
    load
    check [:id]"""

    if len(segments) == 0:
        conn.send([1,helpMsg])
        return

    elif segments[0] == 'get':
        # get all provider
        
        for provider in providers.providers:
            if len(segments) == 1:
                conn.send([0,provider.list()]) 
            else:
                if provider.id == segments[1]:
                    conn.send([0,provider.list()]) 

    elif segments[0] == 'list':
        # get all provider
        for provider in providers.providers:
            conn.send([0,provider.id]) 


    elif segments[0] == 'check':
        for provider in providers.providers:
            if len(segments) == 1:
                conn.send([1,"Missing ID"])
                conn.send([0,helpMsg])
                break
            else:
                if provider.id == segments[1]:
                    # check all ips
                    for ip in provider.IPs:
                        conn.send([0,"checking " + ip + " ..."])
                        provider.checkIP(ip)
                conn.send([0,provider.list()]) 
        
    elif segments[0] == 'save':
        # get all provider
        try:
            providers.writeStats()
            conn.send([0,"\033[92mDone!\033[0m"])
        except:
            conn.send([1,"Error saving state"])

    elif segments[0] == 'load':
        # get all provider
        try:
            providers.readStats()
            conn.send([0,"\033[92mDone!\033[0m"])
        except:
            conn.send([1,"Error lodaing state"])
   
    elif segments[0] == 'help':
        conn.send([0,helpMsg]) 
    else:
        conn.send([1,"Operation not found"])
        conn.send([0,helpMsg])

def cmdModStatus(conn,segments, providers):
    conn.send([1,"status module not implemented!"])