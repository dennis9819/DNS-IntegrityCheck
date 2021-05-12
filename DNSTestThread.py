
from DNSDecodeUDP import processReq
import _thread
import json
import uuid

def testServer(req,server):
    trace_id = uuid.uuid4().hex
    _thread.start_new_thread( testThread, (req, server, trace_id,) )

def testThread(req,server, trace_id):
    
    results = []

    for provider in server.providers.providers:
        p_ip = provider.getIP()
        if len(p_ip) == 0:
            continue

        data = {}

        try:        
            TCPanswer = server.sendTCP(p_ip, req)
            if TCPanswer:
                UDPanswer = TCPanswer[2:]
                data = processReq(req,UDPanswer,p_ip)
        except:
            data = {
                "error": "Timeout",
                "server": p_ip
            }

        results.append(data)
    
    print (json.dumps(results, indent=4, sort_keys=True))
    filename = "debug/trace_{}.json".format(trace_id)
    with open(filename, 'w') as outfile:
        json.dump(results, fp=outfile, indent=4, sort_keys=True )