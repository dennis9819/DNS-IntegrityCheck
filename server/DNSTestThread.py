#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# Author: Dennis Gunia
# Date created: 12.05.2021
# Python Version: 3.6


from DNSPacket import DNSPacket
from typing import ByteString
from DNSProviders import DNSProviderObject, DNSProviders
import socket
import _thread
import json
import uuid
from datetime import datetime


def testServer(req: bytearray,pserver,trace_id):
    # generate new thread
    _thread.start_new_thread( startTest, (req, pserver, trace_id,) )

def startTest(req: bytearray, pserver, trace_id: str):
    testClass = DNSTestServerGroup(pserver,req)
    testClass.checkAll()
    testClass.saveTraceFile(trace_id)
    testClass.analyzeResults(trace_id)

class DNSTestServerInstance:
    def __init__(self,pserver, req:bytearray, provider: DNSProviderObject):
        self.pserver = pserver
        self.provider: DNSProviderObject = provider
        self.req = req
        self.ip = provider.getIP()
        self.rc = 0
        self.error = ""
        self.res: DNSPacket = None
        self.final_ip = "" # only used for analyzer

    def send(self):
        if self.ip == '':
            self.rc = 404
            self.error = "No IP"
        else:
            try:        
                response = self.pserver.proxyServer.sendTCP(self.ip, self.req)
                if response:
                    UDPanswer = response[2:]
                    self.res = DNSPacket(UDPanswer)

            except socket.timeout:
                self.rc = 1
                self.error = "Timeout"
                self.provider.fault(self.ip)
            except ConnectionRefusedError:
                self.rc = 2
                self.error = "Connection Refused"
                self.provider.fault(self.ip)


class DNSTestServerGroup:
    def __init__(self, pserver, req:bytearray):

        self.pserver = pserver
        self.providers = pserver.providers.providers
        self.instances: DNSTestServerInstance = []
        self.req = req
        self.reqParsed = DNSPacket(req)
        # prepare instances
        for providerObj in self.providers:
            self.instances.append(DNSTestServerInstance(self.pserver, self.req, providerObj))

    def checkAll(self):
        for instance in self.instances:
            instance.send()
    
    def getDict(self):
        providers = []
        for instance in self.instances:
            if instance.rc == 0:
                dictObj = {
                    "provider_ip": instance.ip,
                    "provider_name": instance.provider.providerName,
                    "results": instance.res.getDict(),
                    
                }
                providers.append(dictObj)

        dictObj = {
            "request": self.reqParsed.getDict(),
            "providers": providers
        }
        return dictObj
        # print (json.dumps(dictObj, indent=4, sort_keys=True))

    def saveTraceFile(self, trace_id:str ,folder:str = "debug"):
        # dump response to file
        filename = "{}/trace_{}.json".format(self.pserver.config["varPath"] + "/trace/",trace_id)
        with open(filename, 'w') as outfile:
            json.dump(self.getDict(), fp=outfile, indent=4, sort_keys=True )

    def analyzeResults(self,trace_id:str):
        requestType = self.reqParsed.queries[0].type 
        ipTrustValues = {}
        correctIP = ""
        # iterate over all suitable results
        for instance in self.instances:
            if instance.rc != 0:
                continue
            elif instance.res.rcode > 0:
                continue
            else:
                # continue if no error
                for answers in instance.res.answers:
                    if answers.type != requestType:
                        continue
                    else:
                        if answers.type == 1:
                            instance.final_ip = answers.data["IPv4"]  
                        elif answers.type == 28:
                            instance.final_ip = answers.data["IPv6"]
                        else:
                            continue
                        

                        if instance.final_ip in ipTrustValues.keys():
                            ipTrustValues[instance.final_ip] += instance.provider.trustValue
                        else:
                            ipTrustValues[instance.final_ip] = instance.provider.trustValue
                        
                        break
        # only if there are any results
        if len(ipTrustValues) == 0:
            return
        else:
            # select dominating ip
            highest_val = 0
            for trust_ip_obj in ipTrustValues.keys():
                if ipTrustValues[trust_ip_obj] > highest_val:
                    correctIP = trust_ip_obj
                    highest_val = ipTrustValues[trust_ip_obj]

            # process results
            for instance in self.instances:
                if instance.rc != 0:
                    continue
                elif instance.res.rcode > 0:
                    continue
                elif instance.final_ip == correctIP:
                    # likely valid
                    instance.provider.validReq()
                else:
                    # likely manipulated / censsored
                    instance.provider.invalidReq()

            print(ipTrustValues, correctIP)

        self.pserver.providers.writeStats()
        # generate report
        filename = "{}/report_{}.txt".format(self.pserver.config["varPath"] + "/finding/",trace_id)
        f_report = open(filename, 'w')
        f_report.write("DNS Deviation Report - ID : {}\n".format(trace_id))
        f_report.write("Corresponding tracefile : {}\n".format("{}/trace_{}.json".format("findings",trace_id)))
        f_report.write("===============================================================\n\n")
        f_report.write("Request Date    : {}\n".format(datetime.now()))
        f_report.write("Request URL     : {}\n\n".format(self.reqParsed.queries[0].name))
        f_report.write("")    

        # print result ip table
        f_report.write("{:<26}{}\n".format("IP:","TrustScore:"))
        for ip in ipTrustValues.keys():
            f_report.write("{:<26}{}\n".format(ip,ipTrustValues[ip]))  
        f_report.write("\nCorrect IP      : {}\n\n".format(correctIP)) 

        # print deviationg providers
        f_report.write("Deviating Providers:\n{:<26}{:<18}{:<7}{:<6}{:<6}\n".format("Provider:","IP:","Trust:","True:","False:"))
        for instance in self.instances:
            if instance.rc != 0:
                continue
            elif instance.res.rcode > 0:
                continue
            elif instance.final_ip != correctIP:
                f_report.write("{:<26}{:<18}{:<7}{:<6}{:<6}\n".format(
                    instance.provider.providerName,
                    instance.ip,
                    instance.provider.trustValue,
                    instance.provider.reqTrue,
                    instance.provider.reqFalse,
                ))  

        f_report.write("Valid Providers:\n{:<26}{:<18}{:<7}{:<6}{:<6}\n".format("Provider:","IP:","Trust:","True:","False:"))
        for instance in self.instances:
            if instance.rc != 0:
                continue
            elif instance.res.rcode > 0:
                continue
            elif instance.final_ip == correctIP:
                f_report.write("{:<26}{:<18}{:<7}{:<6}{:<6}\n".format(
                    instance.provider.providerName,
                    instance.ip,
                    instance.provider.trustValue,
                    instance.provider.reqTrue,
                    instance.provider.reqFalse,
                ))  

        f_report.close()

