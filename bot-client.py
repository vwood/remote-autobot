#!/usr/bin/env python

import zmq
import time
import autopy
import base64
import zlib

port = 18080

# TODO: auth, using auth object

def send(socket, command):
    done = False
    while not done:
        try:
            socket.send_json(command, zmq.NOBLOCK)
            done = True
        except zmq.ZMQError, e:
            if e.errno != zmq.EAGAIN:
                raise
        time.sleep(0.1)                

def get_response(socket):
    while True:
        try:
            return socket.recv_json(zmq.NOBLOCK)
        except zmq.ZMQError, e:
            if e.errno != zmq.EAGAIN:
                raise
        time.sleep(0.1)
                
context = zmq.Context.instance()
socket = context.socket(zmq.REQ)

machine = raw_input("Connect to? ").strip()
if len(machine) == 0:
    machine = 'localhost'
print "Connecting to %s:%s" % (machine, port)
socket.connect('tcp://%s:%s' % (machine, port))
print "Connected..."

def command_loop(socket):
    done = False
    while not done:
        command = raw_input("> ")
        command = command.strip()
        if len(command) == 0:
            continue
        command = command.split()
        command, args = command[0].lower(), command[1:]

        if command == 'help':
            print "Valid commands:"
            print "  help              - display this help"
            print "  capture [x y w h] - capture a region (or entire screen)"
            print "  mouse x y         - move mouse"
            print "  drag x1 y1 [x2 y2]- drag mouse to x1 y1, or from x1 y1 to x2 y2"
            print "  info              - basic screen info"
            print
        elif command == 'capture':
            send(socket, {"cmd":command, "args":args})
            response = get_response(socket)
            if response.has_key('capture'):
                capture = response['capture']
                capture = autopy.bitmap.Bitmap.from_string(
                    zlib.decompress(base64.b64decode(capture)))
                capture.save("capture.png", "PNG")
                print "saved capture"
            else:
                print "Result missing from capture."
        elif command == 'info':
            send(socket, {"cmd":command, "args":args})
            response = get_response(socket)
            print "INFO:", response["info"]
        else:
            # Will work for commands that don't require anything more for response
            send(socket, {"cmd":command, "args":args})
            response = get_response(socket)
            if response.has_key("error"):
                print "ERROR:", response["error"]

command_loop(socket)
