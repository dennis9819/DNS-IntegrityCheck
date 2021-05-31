#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# Author: Dennis Gunia
# Date created: 30.03.2021
# Python Version: 3.6


from frontends.FeUDP import FrontEnd_UDP
from backends.BeUDP import BackEnd_UDP
from backends.BeDoH import BackEnd_DoH
from backends.BeTCP import BackEnd_TCP
from RedisInterface import RedisConnection


import DNSProviders 
import DNSProxyServer
import sys, getopt
import Logging
import DNSCliServer
import yaml
import _thread
import time

# init logging instance
Logging.logInstance = Logging.Logging()

# define frontend / backend interfaces
backendClasses = [
    BackEnd_TCP,
    BackEnd_UDP,
    BackEnd_DoH
]
frontendClasses = [
    FrontEnd_UDP
]
interfaces = (backendClasses, frontendClasses, {})

#############################################
# MAIN PROG                                 #
#############################################

def printUsage():
    print ('DNSServer.py -c <providerconfig> (-p <dns port>)')

def main(argv):
    providerconfig = ''
    port = 5354
    configFile = "conf.yml"
    config = {}
    try:
        with open(configFile, 'r') as stream:
            try:
                config = yaml.safe_load(stream)
            except yaml.YAMLError as exc:
                Logging.logInstance.logError("Failed to parse config")
                print(exc)
                exit(101)
    except FileNotFoundError as exc:
        Logging.logInstance.logError("Failed to open config")
        print(exc)
        exit(100)

    interfaces = (backendClasses, frontendClasses, config)


    try:
        Logging.logInstance.logfile = config["logpath"]
    except KeyError as exc:
        Logging.logInstance.logError("Invalid logfile config at key " + exc.args[0])
        exit(102)

    # open redis
    try:
        redisServer = RedisConnection(config["redis"]["ip"],config["redis"]["port"])
    except KeyError as exc:
        Logging.logInstance.logError("Invalid redis config at key " + exc.args[0])
        exit(102)

    # load args
    try:
        opts, args = getopt.getopt(argv,"hc:p:",["config=","port="])
    except getopt.GetoptError:
        printUsage()
        sys.exit(2)
    for opt, arg in opts:
        if opt == '-h':
            printUsage()
            sys.exit()
        elif opt in ("-c", "--config"):
            providerconfig = arg
        elif opt in ("-p", "--port"):
            port = arg

    if providerconfig == '':
        printUsage()
        sys.exit(2)

    # load config
    providers = DNSProviders.DNSProviders(redisServer, interfaces)
    providers.loadFromFile(providerconfig)
    providers.readStats()
    providers.writeStats()
    
    _thread.start_new_thread(checkerThread, (providers,))
    # providers.print()
    DNSCliServer.runCliServer(providers)
    
    proxyServer = DNSProxyServer.DNSProxyServer(port,providers, interfaces)
    # start server

    

def checkerThread(providers):
    while True:
        providers.checkInterfaces()
        time.sleep(300000) # every 5 minutes


if __name__ == "__main__":
    main(sys.argv[1:])


