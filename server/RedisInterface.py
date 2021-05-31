#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# Author: Dennis Gunia
# Date created: 18.05.2021
# Python Version: 3.6

import redis

class RedisConnection:

    def __init__(self, ip:str, port:int):
        self.ip = ip
        self.port = port
        self.redis = redis.Redis(host=self.ip, port=self.port, db=0)

    def getConnection(self):
        return self.redis