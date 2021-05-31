#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# Author: Dennis Gunia
# Date created: 30.03.2021
# Python Version: 3.6

#############################################
# MAIN PROG                                 #
#############################################

from PServer import PServer
import getopt
import sys


def printUsage():
    print ('DNSServer.py -c <providerconfig>')

def main(argv):
    # load args

    providerconfig = ''

    try:
        opts, args = getopt.getopt(argv,"hc:",["config="])
    except getopt.GetoptError:
        printUsage()
        sys.exit(2)
    for opt, arg in opts:
        if opt == '-h':
            printUsage()
            sys.exit()
        elif opt in ("-c", "--config"):
            providerconfig = arg

 
    pserver = PServer()
    pserver.loadProvider(providerconfig)
    pserver.readDB()
    pserver.writeDB()
    pserver.startServer()

if __name__ == "__main__":
    main(sys.argv[1:])


