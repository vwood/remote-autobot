#!/usr/bin/env python

import autopy
import zmq
import time
import zlib
import base64

# print autopy.color.hex_to_rgb(0xffffff) 
# print autopy.color.rgb_to_hex(0, 0, 0)

# print screen.find_color(0xffffff, 0.1, None) # color, tolerance, rect
# print screen.count_of_color(0x000000, 0.1, None)

# screen.count_of_bitmap(needle_bmp, tolerance=0.1, rect=None)
# screen.find_bitmap(needle_bmp, tolerance=0.1, rect=None)

# tiny = screen.get_portion((10, 10), (20, 20))
# tiny.save("tiny.png", "PNG")

# autopy.color.hex_to_rgb() # hex to tuple
# autopy.color.rgb_to_hex() # tuple to hex

# autopy.mouse.click(autopy.mouse.LEFT_BUTTON)
# autopy.mouse.click(autopy.mouse.CENTER_BUTTON)
# autopy.mouse.click(autopy.mouse.RIGHT_BUTTON)

# print autopy.mouse.get_pos()

# print autopy.screen.get_color(20, 20)
# print autopy.screen.get_size()


port = 18080

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
sock = context.socket(zmq.REP)
sock.bind('tcp://*:%s' % (port,))

while True:
    message = get_response(sock)
    command = message['cmd']
    args = message["args"]
    result = {"cmd" : command}

    if command == 'capture':
        if len(args) == 4:
            x, y, w, h = [int(arg) for arg in args]
            print "capturing region (%d, %d) (%d, %d)" % (x, y, w, h)
            capture = autopy.bitmap.capture_screen(((x, y), (w, h)))
        else:
            print "capturing whole screen"
            capture = autopy.bitmap.capture_screen()
        capture = capture.to_string()
        capture = base64.b64encode(zlib.compress(capture))
        result["capture"] = capture
    elif command == 'info':
        result["info"] = autopy.screen.get_size()
    elif command == 'mouse':
        if len(args) == 2:
            x, y = [int(arg) for arg in args]
            autopy.mouse.move(x,y)
        else:
            result["error"] = "Error, incorrect args"
    elif command == 'drag':
        if len(args) == 2:
            x2, y2 = [int(arg) for arg in args]
            autopy.mouse.toggle(True, autopy.mouse.LEFT_BUTTON)
            autopy.mouse.smooth_move(x2, y2)
            autopy.mouse.toggle(False, autopy.mouse.LEFT_BUTTON)
        elif len(args) == 4:
            x1, y1, x2, y2 = [int(arg) for arg in args]
            autopy.mouse.move(x1,y1)
            autopy.mouse.toggle(True, autopy.mouse.LEFT_BUTTON)
            autopy.mouse.smooth_move(x2, y2)
            autopy.mouse.toggle(False, autopy.mouse.LEFT_BUTTON)
        else:
            result["error"] = "Error, incorrect args"
    elif command == 'echo':
        print "ECHO: ", ' '.join(args)
    else:
        result["error"] = "Unrecognised command"

    send(sock, result)

