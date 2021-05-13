#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# Author: Dennis Gunia
# Date created: 30.03.2021
# Python Version: 3.6

import proxy_srv.DNSProviders 
import proxy_srv.DNSProxyServer
import sys, getopt

def printUsage():
    print ('DNSServer.py -c <providerconfig> (-p <dns port>)')

def main(argv):
    providerconfig = ''
    port = 5354

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
    providers = proxy_srv.DNSProviders.DNSProviders()
    providers.loadFromFile(providerconfig)
    providers.print()

    proxyServer = proxy_srv.DNSProxyServer.DNSProxyServer(port,providers)
    # start server


if __name__ == "__main__":
    main(sys.argv[1:])


