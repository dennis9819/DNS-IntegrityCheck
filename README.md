#DNS Integrity Server 

This server acts as an DNS "Proxy" and transparently forwards the request to an specified server. The answer ist then sent back to the requestiing client.
In addition to that, the server takes a list of other DNS-Servers and forwards the request to these as well. The results are now stored in ./debug.
In the future, the server will be able to check the results and detect possible DNS-level censoring or manipulation.

For this project, the proxy is required to receive queries in UDP mode, which is the default transport protocol for DNS. However, for forwarding query to a DNS server, TCP should be used by the proxy.  No caching capacity is required.  

The proxy should only forward valid DNS request. For incoming UDP packets that do not have a valid DNS header, those packets should be discarded.

This is a side-project I do for fun. I know that this design has some flaws.

## Run Server
For Testing:
    python3 DNSServer.py -c <path to config>

The server runs on Port 5354

## Config-File
The Config-File contains all DNS-Servers that should be checked.

The Syntax is very easy. The File is organized into blocks.
Each block represents one provider. Each provider can have multiple DNS-Servers.
When starting, the script pings all servers and determins the fastest server for each block. This server is then marked as the primary server and is used for checking. The other servers are marked as "standby".

The Primary DNS-Server is marked with $master
Example:
    # this is a comment
    [CloudFlare] # define new provider
    $master      # mark provider as primary
    1.1.1.1      # add DNS-Server

It is also possible to define an aliad/comment.

    [Deutsche Telekom AG]
    217.5.100.185: Deutsche Telekom AG
    217.5.100.186: Deutsche Telekom AG


## Sources
* (http://www.tcpipguide.com/free/t_DNSMessageHeaderandQuestionSectionFormat.htm)
* (http://www.tcpipguide.com/free/t_DNSMessageResourceRecordFieldFormats.htm)
* (http://doc-tcpip.org/Dns/named.dns.message.html)
* (https://www.iana.org/assignments/dns-parameters/dns-parameters.xhtml)
* (https://datatracker.ietf.org/doc/html/rfc1035)
* (http://www.tcpipguide.com/free/t_DNSNameNotationandMessageCompressionTechnique.htm)