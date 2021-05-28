# DNS Integrity Server 

This server acts as an DNS "Proxy" and transparently forwards the request to an specified server. The answer ist then sent back to the requestiing client.
In addition to that, the server takes a list of other DNS-Servers and forwards the request to these as well. The results are now stored in ./debug.
In the future, the server will be able to check the results and detect possible DNS-level censoring or manipulation.

For this project, the proxy is required to receive queries in UDP mode, which is the default transport protocol for DNS. However, for forwarding query to a DNS server, TCP should be used by the proxy.  No caching capacity is required.  

The proxy should only forward valid DNS request. For incoming UDP packets that do not have a valid DNS header, those packets should be discarded.

This is a side-project I do for fun. I know that this design has some flaws.

## Run Server
For Testing:

    python3 DNSServer.py -c <path to config>


## Provider-File
The Provider-File contains all DNS-Servers that should be checked.

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

## Config-File
The configuration file contains all nearly all informations that are requierd to run the proxy server.

This includes:
* logfile path
* redis configuration (ip & port)
* frontend configuration
* backend configuaration

### logpath
The logpath variable contains the logfile-path.

    logpath: "./dnsproxy.log"

### redis
Redis contains the `ip` and `port` of the redis server.

    redis:
      ip: 127.0.0.1
      port: 6379 

### frontend
All modules which take requests are configured in the frontend section.

    frontend:
      fe1:
        type: "udp"
        host: "0.0.0.0"
        port: 5355
      fe2:
        type: "udp"
        host: "0.0.0.0"
        port: 5356

`fe1` and `fe2` are customizable names. You can configure as many frontends as you want.
Every frontend needs at least the type parameter. This specifies the frontend type.
Currently there is only:
* `udp`

All other parameters are frontend-specific.

#### **frontend-udp**
* `host` -> listening ip address
* `port` -> listening port

### backend
All modules which forward requests are configured in the backend section.

    backend:
      be1:
        type: "tcp"   # DNS over TCP

      be2:
        type: "udp"   # DNS over UDP
        delay: 3
        timeout: 3000

      be3:
        type: "doh"   # DNS over HTTPS
        master: true
        url: "dns-query"

`be1`, `be2`,... are customizable names as well. You can configure as many backend as you want.
Every backend needs at least the type parameter. This specifies the frontend type.

Currently there are:
* `udp` -> DNS over UDP/53
* `tcp` -> DNS over TCP/53
* `doh` -> DNS over HTTPS/443 (RFC8484) (non json)

The primary backend is specified by `master: true`

All other parameters are backend-specific.

The priority is specified by the `protoPriority` list.

#### **backend-udp**
* `delay` -> delay between retries
* `timeout` -> timeout for answer

#### **backend-tcp**
no additional parameters

#### **backend-doh**
* `url` -> url-path

Example: `https://1.1.1.1/\<urlpath\>?dns=....`

## Redis
The redis-database can be used to store trust values and server states. It it planned to also implement a DNS cache.

## CLI
TODO: Write Doc

## Sources
* http://www.tcpipguide.com/free/t_DNSMessageHeaderandQuestionSectionFormat.htm
* http://www.tcpipguide.com/free/t_DNSMessageResourceRecordFieldFormats.htm
* http://doc-tcpip.org/Dns/named.dns.message.html
* https://www.iana.org/assignments/dns-parameters/dns-parameters.xhtml
* https://datatracker.ietf.org/doc/html/rfc1035
* http://www.tcpipguide.com/free/t_DNSNameNotationandMessageCompressionTechnique.htm
### DoH
* https://datatracker.ietf.org/doc/html/rfc8484#section-4.1
* https://developers.google.com/speed/public-dns/docs/doh
* https://developers.cloudflare.com/1.1.1.1/dns-over-https/request-structure