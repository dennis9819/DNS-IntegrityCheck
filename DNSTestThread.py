#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# Author: Dennis Gunia
# Date created: 12.05.2021
# Python Version: 3.6

from typing import ByteString
from DNSProviders import DNSProviders
import time
import socket
from DNSDecodeUDP import decodeResponse, processReq
import _thread
import json
import uuid
import sys
from datetime import datetime


def testServer(req: bytearray,server: DNSProviders):
    # generate new thread
    trace_id = uuid.uuid4().hex
    _thread.start_new_thread( testThread, (req, server, trace_id,) )

def testThread(req: bytearray, server: DNSProviders, trace_id: str):
    
    results = []    # contains all query responses
    request = decodeResponse(req, "127.0.0.1")
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
            provider.fault(p_ip)
        except ConnectionRefusedError:
            data = {
                "error": "Connection Refused",
                "server": p_ip
            }
            provider.fault(p_ip)
        #except:
        #    print("Unexpected error:", sys.exc_info()[0])
        #    data = {
        #        "error": "Unexpected Error",
        #        "server": p_ip
        #    }            
        results.append(data)
    
        result_body = {
            "results": results,
            "trace_id": trace_id,
            "request_time": time.time(),
            "request": request,
        }

        saveTraceFile(result_body,result_body["trace_id"])
    # server.providers.print()
    # print (json.dumps(results, indent=4, sort_keys=True))
    analyzeResults(request,results,server)

    
def saveTraceFile(data:dict ,trace_id:str ,folder:str = "debug"):
    if False:
        return
    else:
        # dump response to file
        filename = "{}/trace_{}.json".format(folder,trace_id)
        with open(filename, 'w') as outfile:
            json.dump(data, fp=outfile, indent=4, sort_keys=True )

def analyzeResults(req:dict, results:dict, server:DNSProviders):
    # print (json.dumps(data, indent=4, sort_keys=True))
    r_type = req["Q_0"]["QTYPE"]
    # print(r_type)

    # process data
    responses = {}
    ips = {}
    providers = {}
    trusts = {}
    for result in results:
        if "error" in result:
            continue
        elif result["f_rcode"] > 0:
            continue
        else:
            for response in result.keys():
                if response[0:3] == 'RR_' and result[response]["QTYPE"] == r_type:
                    ip = ""
                    if r_type == 1:
                        ip = result[response]["RDATA_IPv4"]  
                    elif r_type == 28:
                        responses[result["server"]] = result[response]["RDATA_IPv6"]
                    else:
                        continue

                    responses[result["server"]] = ip
                    provider_obj = server.providers.getProvider(result["server"])
                    provider = provider_obj.providerName
                    trust = provider_obj.trustValue
                    # add ip to ips
                    if ip in ips.keys():
                        ips[ip] += 1
                    else:
                        ips[ip] = 1

                    # create providers array
                    provider_obj={
                            "ip": result["server"],
                            "provider": provider,
                            "provider_obj": provider_obj,
                    }
                    if ip in providers.keys():
                        providers[ip].append(provider_obj)
                    else:
                        providers[ip] = [provider_obj]
                    
                    # calculate trust sum
                    if ip in trusts.keys():
                        trusts[ip] += trust
                    else:
                        trusts[ip] = trust

                else:
                    continue

    # determine deveating dns servers
    highest_ip = ""
    highest_val = 0
    for trust_ip_obj in trusts.keys():
        if trusts[trust_ip_obj] > highest_val:
            highest_ip = trust_ip_obj
            highest_val = trusts[trust_ip_obj]

    # process deviating providers
    for provider in providers.keys():
        if provider != highest_ip:
            # change trust and update values
            for provider_item in providers[provider]:
                provider_item["provider_obj"].invalidReq()
                provider_item["trustValue"] =  provider_item["provider_obj"].trustValue
                provider_item["reqTrue"] = provider_item["provider_obj"].reqTrue
                provider_item["reqFalse"] = provider_item["provider_obj"].reqFalse
                del provider_item["provider_obj"]

        else:
            for provider_item in providers[provider]:
                provider_item["provider_obj"].validReq()
                provider_item["trustValue"] =  provider_item["provider_obj"].trustValue
                provider_item["reqTrue"] = provider_item["provider_obj"].reqTrue
                provider_item["reqFalse"] = provider_item["provider_obj"].reqFalse
                del provider_item["provider_obj"]

    if len(responses.keys()) > 0:
        if len(ips.keys()) > 1:
            finding_obj = {
                "correct_ip": highest_ip,
                "trusts": trusts,
                "trace" : results,
                "responses": responses,
                "provider": providers,
                "ips": ips,
            }
            trace_id = uuid.uuid4().hex
            saveTraceFile(finding_obj,trace_id,"findings")
            genReport(req,finding_obj,server,trace_id)


def genReport(req:dict, finding_obj:dict, server:DNSProviders, trace_id:str):
    filename = "{}/report_{}.txt".format("findings",trace_id)
    f_report = open(filename, 'w')
    f_report.write("DNS Deviation Report - ID : {}\n".format(trace_id))
    f_report.write("Corresponding tracefile : {}\n".format("{}/trace_{}.json".format("findings",trace_id)))
    f_report.write("===============================================================\n\n")
    f_report.write("Request Date    : {}\n".format(datetime.now()))
    f_report.write("Request URL     : {}\n\n".format(req["Q_0"]["QNAME"]))
    f_report.write("")    
    # print result ip table
    f_report.write("{:<26}{}\n".format("IP:","TrustScore:"))
    for ip in finding_obj["trusts"].keys():
        f_report.write("{:<26}{}\n".format(ip,finding_obj["trusts"][ip]))  
    f_report.write("\nCorrect IP      : {}\n\n".format(finding_obj["correct_ip"])) 

    # print seviationg providers

    f_report.write("Deviating Providers:\n{:<26}{:<18}{:<7}{:<6}{:<6}\n".format("Provider:","IP:","Trust:","True:","False:"))
    for ip in finding_obj["provider"].keys():
        if ip == finding_obj["correct_ip"]:
            continue
        else:
            for provider_obj in finding_obj["provider"][ip]:
                f_report.write("{:<26}{:<18}{:<7}{:<6}{:<6}\n".format(
                    provider_obj["provider"],
                    provider_obj["ip"],
                    provider_obj["trustValue"],
                    provider_obj["reqTrue"],
                    provider_obj["reqFalse"],
                ))  
    f_report.write("Valid Providers:\n{:<26}{:<18}{:<7}{:<6}{:<6}\n".format("Provider:","IP:","Trust:","True:","False:"))
    for ip in finding_obj["provider"].keys():
        if ip != finding_obj["correct_ip"]:
            continue
        else:
            for provider_obj in finding_obj["provider"][ip]:
                f_report.write("{:<26}{:<18}{:<7}{:<6}{:<6}\n".format(
                    provider_obj["provider"],
                    provider_obj["ip"],
                    provider_obj["trustValue"],
                    provider_obj["reqTrue"],
                    provider_obj["reqFalse"],
                ))  

    f_report.close()
