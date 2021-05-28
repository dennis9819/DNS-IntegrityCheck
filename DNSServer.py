#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# Author: Dennis Gunia
# Date created: 30.03.2021
# Python Version: 3.6


from RedisInterface import RedisConnection
import DNSProviders 
import DNSProxyServer
import sys, getopt
import Logging
import DNSCliServer
import yaml

Logging.logInstance = Logging.Logging()

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
    providers = DNSProviders.DNSProviders(redisServer)
    providers.loadFromFile(providerconfig)
    providers.readStats()
    providers.writeStats()
    # providers.print()

    DNSCliServer.runCliServer(providers)
    
    proxyServer = DNSProxyServer.DNSProxyServer(port,providers, config)
    # start server


if __name__ == "__main__":
    main(sys.argv[1:])


