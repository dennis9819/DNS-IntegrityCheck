from DNSQueryTypes import DNSQueryType
import binascii


def processReq(query,response,server):
    # decodeQuery(query)
    return decodeResponse(response,server)

#def decodeQuery(data):
    #print ("[REQ] RAW: ", binascii.hexlify(data))

def decodeResponse(data,server):
    decodedData = {}
    #print ("[RES] RAW: ", binascii.hexlify(data))
    # decode message
    f_ident = data[0:2]
    f_controll = data[2:4]
    f_question = data[4:6]
    f_answer = data[6:8]
    f_authority = data[8:10]
    f_additional = data[10:12]

    #print(int.from_bytes(f_question, "big"))
    #print(int.from_bytes(f_answer, "big"))
    #print(int.from_bytes(f_authority, "big"))
    #print(int.from_bytes(f_additional, "big"))
    decodedData["server"] = server
    decodedData["f_id"] = f_ident
    decodedData["f_question"] = int.from_bytes(f_question, "big")
    decodedData["f_answer"] = int.from_bytes(f_answer, "big")
    decodedData["f_authority"] = int.from_bytes(f_authority, "big")
    decodedData["f_additional"] = int.from_bytes(f_additional, "big")

    # get response code
    decodedData["f_rcode"] = f_controll[1] & 0x0F

    f_payload = data[12:] 
    #debugHexDump (f_payload)

    # process question
    # length is multiple of 2 (16-bit) -> http://www.tcpipguide.com/free/t_DNSMessageHeaderandQuestionSectionFormat-2.htm
    f_QDCOUNT = int.from_bytes(f_question, "big")
    m_offset = 0x00
    f_count = 0
    while f_QDCOUNT > 0:
        dict_item = "Q_{}".format(f_count)
        f_count += 1
        decodedData[dict_item] = {}
        m_len = int.from_bytes(f_payload[m_offset:m_offset +1], "big")
        m_offset += 1
        m_domain_string = ""
        while(m_len > 0):
            m_qname = f_payload[(m_offset):(m_offset + m_len)]
            m_offset += m_len
            m_len = int.from_bytes(f_payload[m_offset:m_offset +1], "big")
            m_offset += 1
            if len(m_domain_string) > 0:
                m_domain_string += "."
            m_domain_string += m_qname.decode("utf-8")
            

        m_qtype = int.from_bytes(f_payload[(m_offset ):(m_offset + 2)], "big")
        m_offset += 2
        m_qclass = int.from_bytes(f_payload[(m_offset):(m_offset + 2)], "big")
        m_offset += 2

        decodedData[dict_item]["QTYPE"] = m_qtype
        decodedData[dict_item]["QCLASS"] = m_qclass
        decodedData[dict_item]["QTYPE_RES"] = DNSQueryType[m_qtype]
        decodedData[dict_item]["QNAME"] = m_domain_string

        #print("Query:" , m_domain_string, DNSQueryType[m_qtype], m_qclass)
        f_QDCOUNT -= 1

    # process answer
    f_ANCOUNT = int.from_bytes(f_answer, "big")
    #debugHexDump (f_payload[(m_offset):])

    f_count = 0
    while f_ANCOUNT > 0:
        dict_item = "RR_{}".format(f_count)
        f_count += 1
        decodedData[dict_item] = {}

        m_offset += 2
        #debugHexDump (f_payload[(m_offset):])

        m_qtype = int.from_bytes(f_payload[(m_offset ):(m_offset + 2)], "big")
        m_offset += 2
        m_qclass = int.from_bytes(f_payload[(m_offset):(m_offset + 2)], "big")
        m_offset += 2
        decodedData[dict_item]["QTYPE"] = m_qtype
        decodedData[dict_item]["QCLASS"] = m_qclass
        decodedData[dict_item]["QTYPE_RES"] = DNSQueryType[m_qtype]

        #print("RES:" , DNSQueryType[m_qtype], m_qclass)

        m_ttl = int.from_bytes(f_payload[m_offset:m_offset +4], "big")
        m_offset += 4
        m_rlen = int.from_bytes(f_payload[m_offset:m_offset +2], "big")
        m_offset += 2

        decodedData[dict_item]["TTL"] = m_ttl

        m_data = f_payload[(m_offset):(m_offset + m_rlen)]
        decodedData[dict_item]["RDATA"] = m_data.decode('ASCII', errors="ignore")
        m_offset += m_rlen
        #print (m_ttl, m_rlen,m_data)
        f_ANCOUNT -= 1

        m_ip = "{}.{}.{}.{}".format(int(m_data[0]),int(m_data[1]),int(m_data[2]),int(m_data[3]))
        if m_qtype == 1:
            #print("IP:", m_ip)
            decodedData[dict_item]["RDATA_IPv4"] = m_ip

    return decodedData

def debugHexDump(data):
    d_size = len(data)
    offest = 0x00
    while (offest < d_size):
        d_seg = data[offest:offest+16]
        offest += 16;

        #print line
        d_lineval = "{0:#0{1}x}".format(offest,10)
        print(d_lineval[2:], end='  ')
        index = 0

        for d_byte in d_seg:
            d_hexval= "{0:#0{1}x}".format(d_byte,4)
            print(d_hexval[2:], end=' ')
            index += 1
            if index == 8:
                print(' ', end='')

        # pad missing bytes
        while index < 16:
            print('  ', end=' ')
            index += 1
            if index == 8:
                print(' ', end='')

        # print ascii
        print ("|{}|".format(""))

  