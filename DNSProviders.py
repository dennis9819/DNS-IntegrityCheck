#import pyping
import socket
import os
import subprocess
from subprocess import DEVNULL, STDOUT, check_call
import re

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


class DNSProviderObject:
    ipCount = 0 # amount of imported ips for this specific provider
    def __init__(self, providerName):
        self.providerName = providerName
        self.IPs = []
        self.comments = []
        self.state = []
        self.ping = []
        self.isMaster = []
        self.id = providerName.replace(' ','').lower()
        self.timeRegex = '^.*time\ '
        self.master = False
        self.masterIP = ''
    # check if ip is reachable and set the corresponding state
    def checkIP(self, IP):
        index = self.IPs.index(IP)
        if index == -1:
            raise RuntimeError('IP not imported')

    
        p = subprocess.Popen(['ping', '-c', '1' ,'-W', '0.2', IP], stdout = subprocess.PIPE)
        outLines = p.communicate()[0].decode("utf-8").splitlines()
        if len(outLines) < 6:
            self.state[index] = False
            return

        timeLine = outLines[5]
        timeSubStr = timeLine[23:-3].split('/')
        self.state[index] = True
        self.ping[index] = float(timeSubStr[1])

    # add ip to Provider and check state
    def addIP(self, ip, comment):
        # print("[INFO]    Adding IP: {} - Comment: {} - Provider: {}".format(ip, comment, self.providerName))
        self.IPs.append(ip)
        self.comments.append(comment)
        self.state.append(False)
        self.isMaster.append(False)
        self.ping.append(-1)
        self.ipCount += 1
        # Check if Server is reachable
        self.checkIP(ip)

    def getIP(self):
        return self.masterIP

    def selectMaster(self):
        if len(self.isMaster) == 0:
            return
        lowestID = 0
        lowesValue = 10000
        count = 0
        for ping in self.ping:
            self.isMaster[count] = False
            if ping < lowesValue and ping > -1:
                lowesValue = ping
                lowestID = count
            count += 1
        self.isMaster[lowestID] = True
        self.masterIP = self.IPs[lowestID]

    # debug print object content
    def print(self):
        print( bcolors.BOLD + "==> Provider Info for " + bcolors.OKBLUE + self.providerName + bcolors.ENDC)
        if self.master:
            print("    id: " + bcolors.OKBLUE + self.id + bcolors.ENDC + "  |  " + bcolors.WARNING + "MASTER-Provider" + bcolors.ENDC)
        else:
            print("    id: " + bcolors.OKBLUE + self.id + bcolors.ENDC)
        count = 0
        print(bcolors.BOLD + "server            state    ping      role      desc"+ bcolors.ENDC)
        for server in self.IPs:
            rowFormat = "{:<18}{:<10}{:>10} {:<10}{:<30}"
            state = bcolors.FAIL + "OFFLINE " + bcolors.ENDC
            master = ""
            if self.isMaster[count]:
                master = "*master"
            ping = "∞"
            if self.ping[count] > -1:
                ping = "{} ms".format(self.ping[count])
            if self.state[count]:
                state = bcolors.OKGREEN + "ONLINE  " + bcolors.ENDC
            row = rowFormat.format(server, state, ping, master, self.comments[count])
            print(row)
            count += 1
        if count == 0:
            print(bcolors.WARNING + "  -- no server for this provider --" + bcolors.ENDC)
        
        print("")

class DNSProviders:
    def __init__(self):
        self.providers = []
        self.master = None

    # load provider config
    def loadFromFile(self,file):
        currentSection = ''

        configFile = open(file, 'r')
        configFileLines = configFile.readlines()

        count = 0
        # Strips the newline character
        for line in configFileLines:
            count += 1
            strippedLine = line.strip()
            if strippedLine.startswith("#") or strippedLine == '':
                continue
            
            if strippedLine.startswith("[") and strippedLine.endswith("]"):
                currentSection = strippedLine[1:-1]
                self.providers.append(DNSProviderObject(currentSection))
                continue

            if strippedLine.startswith("$"):
                if strippedLine == "$master":
                    # remove old master
                    if not self.master == None:
                        self.master.master = False
                    # set new master
                    self.providers[-1].master = True
                    self.master = self.providers[-1]
                continue
            
            # split if it has comments
            splitIndex = strippedLine.find(':')
            ip = strippedLine
            comment = ''

            if splitIndex > -1:
                # comment
                ip = strippedLine[0:splitIndex].strip()
                comment = strippedLine[splitIndex + 1:].strip()

            # verify IP
            try:
                socket.inet_aton(ip)
            except:
                print("[WARNING] Line{}: loading config - invalid IP address : {} - ignoring".format(count,ip)) 
                continue

            self.providers[-1].addIP(ip, comment)
        for provider in self.providers:
            provider.selectMaster()
    
    def print(self):
        for provider in self.providers:
            provider.print()


