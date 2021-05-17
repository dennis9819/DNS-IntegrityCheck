

from DNSQueryTypes import DNSQueryType, DNSRespoonseCodes, DNSClasses

class DNSPacket:
    def __init__(self, data:bytearray = None):
        self.raw = data

        # init empty object
        self.ident = 0
        self.controll = 0x0000   
        self.question = 0   
        self.answer = 0      
        self.authority = 0   
        self.additional = 0 

        self.rcode = 0x00
        self.rcode_string = ""

        self.queries: DNSPacketQuery = []
        self.answers: DNSPacketAnswer = []

        if data is not None:
            self.decode(data)

    def decode(self, data:bytearray):
        self.raw = data
         # decode message
        self.ident = int.from_bytes(data[0:2], "big")         # first 2 octets are ID
        self.controll = data[2:4]                             # 2 octets are for status stuff
        self.question = int.from_bytes(data[4:6], "big")      # 2 octets (Question Count)
        self.answer = int.from_bytes(data[6:8], "big")        # 2 octets (Answer Record Count)
        self.authority = int.from_bytes(data[8:10], "big")    # 2 octets (Authority Record Count)
        self.additional = int.from_bytes(data[10:12], "big")  # 2 octets (Additional Record Count)
        # get response code
        self.rcode = self.controll[1] & 0x0F
        self.rcodeString = DNSRespoonseCodes[self.controll[1] & 0x0F]
        # extract payload from package
        offset = 12
        offset = self.__decodeQuestion__(data,offset)
        offset = self.__decodeAnswer__(data,offset)
        # TODO: decodeAuthority
        # TODO: decodeAdditional

    def __decodeQuestion__(self, data:bytearray, start:int):
        offset = start
        couter = 0
        while couter < self.question:  
            # create obj
            __queryObj__ = DNSPacketQuery()

            # read length of first domain part
            sectionLength = int.from_bytes(data[offset:offset +1], "big")
            offset += 1
            domainString = ""
            while(sectionLength > 0): # as long as next part size is bigger than 0 (terminated by len==0x00)
                # extract string
                name = data[offset:(offset + sectionLength)]
                offset += sectionLength
                # read length of next domain part
                sectionLength = int.from_bytes(data[offset:offset +1], "big")
                offset += 1
                # build string
                if len(domainString) > 0:
                    domainString += "."
                domainString += name.decode("utf-8")

            # fill obj data
            __queryObj__.name = domainString
            __queryObj__.type = int.from_bytes(data[offset:(offset + 2)], "big")
            __queryObj__.typeString = DNSQueryType[__queryObj__.type]
            offset += 2
            __queryObj__.dclass = int.from_bytes(data[offset:(offset + 2)], "big")
            __queryObj__.dclassString = DNSClasses[__queryObj__.dclass]
            offset += 2

            # add and next
            couter += 1
            self.queries.append(__queryObj__)

        return offset

    def __decodeAnswer__(self, data:bytearray, start:int):
        offset = start
        couter = 0
        while couter < self.answer:  
            # create obj
            __answerObj__ = DNSPacketAnswer()

            offset += 2 # don know why the heck I need to ignore these two bytes?!?!
                        # won't work without!

            # fill obj data
            __answerObj__.type = int.from_bytes(data[offset:(offset + 2)], "big")
            __answerObj__.typeString = DNSQueryType[__answerObj__.type]
            offset += 2
            __answerObj__.dclass = int.from_bytes(data[offset:(offset + 2)], "big")
            __answerObj__.dclassString = DNSClasses[__answerObj__.dclass]
            offset += 2    
            __answerObj__.ttl = int.from_bytes(data[offset:(offset + 4)], "big")
            offset += 4
            __answerObj__.dataLength = int.from_bytes(data[offset:(offset + 2)], "big")
            offset += 2    
            dataStartOffset = offset
            __answerObj__.dataRaw = data[offset:(offset + __answerObj__.dataLength)]
            offset += __answerObj__.dataLength

            # process types
            __answerObj__.data["hex"] =  __answerObj__.dataRaw.hex()
            # If Question Type of Response is A-Record, parse IP to string
            if __answerObj__.type == 1:    # A
                m_ip = "{}.{}.{}.{}".format(int(__answerObj__.dataRaw[0]),int(__answerObj__.dataRaw[1]),int(__answerObj__.dataRaw[2]),int(__answerObj__.dataRaw[3]))
                __answerObj__.data["RDATA_IPv4"] = m_ip
            elif __answerObj__.type == 28: # AAA
                ip_block=8
                ip_string=""
                while ip_block > 0:
                    ip_block -= 1
                    if ip_block < 7:
                        ip_string += ":"
                    byte_start = (7-ip_block) * 2
                    byte_end = byte_start + 2
                    ip_block_bytes = __answerObj__.dataRaw[byte_start:byte_end]
                    ip_block_int = int.from_bytes(ip_block_bytes, "big")
                    ip_string += ("{0:#0{1}x}".format(ip_block_int,6))[2:]
                __answerObj__.data["RDATA_IPv6"] = ip_string
            elif __answerObj__.type == 2:   # NS
                __answerObj__.data["RDATA_NS"] = self.__decompressURL(self.raw,dataStartOffset)
            elif __answerObj__.type == 5:   # CNAME
                __answerObj__.data["RDATA_CNAME"] = self.__decompressURL(self.raw,dataStartOffset)

            # add and next
            couter += 1
            self.answers.append(__answerObj__)
        return offset

    # generate json ready dict
    def getDict(self):
        dict = self.__dict__.copy()
        del dict["raw"]
        del dict["controll"]
        dict["queries"] = []
        dict["answers"] = []
        for item in self.__dict__["queries"]:
            dict["queries"].append(item.getDict())
        for item in self.__dict__["answers"]:
            dict["answers"].append(item.getDict())
            if "dataRaw" in dict["answers"][-1].keys():
                del dict["answers"][-1]["dataRaw"]
        return dict


    # decompress domain based on RFC 1035 4.1.4
    def __decompressURL(self, data: bytearray, start: int, maxIterationDepth = 32):
        offset = start
        iteration = 0
        domainString = ""
        while iteration < maxIterationDepth:
            iteration += 1
            # get first byte
            segmentLength = int.from_bytes(data[offset:offset+1], "big")
            offset += 1
            # check if pointer
            if segmentLength & 0xC0 > 0:
                # if pointer, change offset to specified octet
                pointerLocation = data[offset-1:offset+1] 
                offset = int.from_bytes(pointerLocation, "big") & 0x3FFF
                continue
            else:
                # if not pointer, check if last element (length = 0)
                if segmentLength == 0:
                    break
                else:
                    # of not pointer nor last, add segment to domainString
                    domain = data[offset:(offset + segmentLength)]
                    offset += segmentLength
                    if len(domainString) > 0:
                        domainString += "."
                    domainString += domain.decode("utf-8")
                    continue
        return domainString

class DNSPacketQuery:
    def __init__(self):
        self.type = 0
        self.dclass = 0
        self.dclassString = ""
        self.typeString = ""
        self.name = ""

    def getDict(self):
        return self.__dict__

class DNSPacketAnswer:
    def __init__(self):
        self.type = 0
        self.dclass = 0
        self.dclassString = ""
        self.typeString = ""
        self.name = ""
        self.ttl = 0
        self.data = {}
        self.dataRaw = b''
        self.dataLength = 0

    def getDict(self):
        return self.__dict__