#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# Author: Dennis Gunia
# Date created: 28.05.2021
# Python Version: 3.6

import datetime
import _thread
import os

class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

class Logging:
    
    def __init__(self,logfile = ""):
        self.logfile = logfile
    

    def writeLog(self,line):
        if self.logfile != "":
            with open(self.logfile, "a") as myfile:
                myfile.write(line + "\n")
                myfile.flush()

    def writeStart(self):
        self.writeLog("===")
        self.logStartup("Starting application with PID " + str(os.getpid()))
        self.logStartup("Running as user " + str(os.getuid()))
        self.logStartup("Main Thread " + self.getThreadId())
        
    def getThreadId(self):
        return str(_thread.get_native_id())
        return str(_thread.get_ident())

    def logStartup(self,message):
        dateStr = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(dateStr + " " + message)
        self.writeLog(dateStr + " " + message)

    def logInfo(self,message):
        dateStr = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(dateStr + " [INFO  ] "+ message)
        self.writeLog(dateStr + " [INFO  ] " + self.getThreadId() + " " + message)

    def logWarning(self,message):
        dateStr = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(dateStr + bcolors.WARNING + " [WARN  ] " + bcolors.ENDC + message)
        self.writeLog(dateStr + " [WARN  ] "+ self.getThreadId() + " " + message)

    def logError(self,message):
        dateStr = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(dateStr + bcolors.FAIL + " [ERROR ] " + bcolors.ENDC + message)
        self.writeLog(dateStr + " [ERROR ] "+ self.getThreadId() + " " + message)

    def logNotice(self,message):
        dateStr = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(dateStr + bcolors.OKBLUE + " [NOTICE] " + bcolors.END + message)
        self.writeLog(dateStr + " [NOTICE] "+ self.getThreadId() + " " + message)

