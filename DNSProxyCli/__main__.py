#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# Author: Dennis Gunia
# Date created: 26.05.2021
# Python Version: 3.6
from multiprocessing.connection import Client
from buffer import HistoryBuffer
import sys, tty, termios
import os
import readline
import atexit

SERVER_IP = 'localhost'
SERVER_PORT = 6000

print('\033[1m\033[95mDNSProxy CLI v0.0.1 - 2021/05/26\033[0m')
print("Trying to connect to Server on {}:{}".format(SERVER_IP,SERVER_PORT))



histfile = os.path.join(os.path.expanduser("~"), ".dnshist")
try:
    readline.read_history_file(histfile)
    readline.set_history_length(9000)
except IOError:
    pass


atexit.register(readline.write_history_file, histfile)


class SimpleCompleter:

    def __init__(self, options):
        self.options = sorted(options)
        self.options2 = sorted(["get", "list", "save", "load", "check"])

    def complete(self, text, state):
        response = None
        if state == 0:
            # This is the first time for this text,
            # so build a match list.
            if text:
                #print("Try ", text)
                self.matches = [
                    s
                    for s in self.options
                    if s and s.startswith(text)
                ]
              
            else:
                #print("Try ", state)
                self.matches = self.options[:]


        # Return the state'th item from the match list,
        # if we have that many.
        try:
            response = self.matches[state]
        except IndexError:
            response = None

        return response


def input_loop():
    line = ''
    while line != 'stop':
        line = input('Prompt ("stop" to quit): ')
        print('Dispatch {}'.format(line))


# Register the completer function
OPTIONS = ['help', 'providers', 'status']
readline.set_completer(SimpleCompleter(OPTIONS).complete)
readline.parse_and_bind('tab: complete')

def readLine():
    return input('\033[94m> \033[0m')

try:
    address = (SERVER_IP, SERVER_PORT)
    conn = Client(address, authkey=b'secret password')
    # get server version
    conn.send('getver')
    msg = conn.recv()
    print("Connected! Server-Version: {}\n\nUse command 'exit' to close CLI.\n".format(msg[0]))


except ConnectionRefusedError:
    print("Conenction Refused!")
    exit(1)


while True:
    
    line = "cmd:{}".format(readLine())
    #line = "cmd:{}".format(input('\033[94m> \033[0m'))
    #buffer.append(line)
    conn.send(line)
    if line == "cmd:exit":
        break
    else:
        while True:
            msg = conn.recv()
            if msg[0] == 9999:
                break
            elif msg[0] == 0:
                # success
                print(msg[1])
            else:
                # error
                print("\033[93m{}\033[0m".format(msg[1]))

conn.close()