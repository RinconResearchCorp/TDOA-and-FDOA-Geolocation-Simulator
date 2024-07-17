#!/usr/bin/python3
# -*- coding: utf-8 -*-

# zmq_PUSH_PULL_server.py

import sys
import pmt
import zmq

_debug = 0

# create a PULL socket
context = zmq.Context()
socket = context.socket(zmq.SUB)
socket.connect("tcp://127.0.0.1:5001") # connect, not bind, the PUB will bind, only 1 can bind
socket.setsockopt(zmq.SUBSCRIBE, b'') # subscribe to topic of all (needed or else it won't work)

while True:
    if socket.poll(10) != 0: # check if there is a message on the socket
        msg = socket.recv()
        msg = pmt.deserialize_str(msg)
        print("Received request: %s\n" % msg)

