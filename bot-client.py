import zmq
import time
import autopy

# screen.save("output.png", "PNG")

port = 18080

def send_command(socket, command):
    done = False
    while not done:
        try:
            sock.send_json(command, zmq.NOBLOCK)
            done = True
        except zmq.ZMQError, e:
            if e.errno != zmq.EAGAIN:
                raise
        time.sleep(0.1)                

def get_response(socket):
    while True:
        try:
            return sock.recv_json(zmq.NOBLOCK)
        except zmq.ZMQError, e:
            if e.errno != zmq.EAGAIN:
                raise
        time.sleep(0.1)

                
context = zmq.Context.instance()
sock = context.socket(zmq.REQ)

machine = raw_input()
print "Connecting to %s:%s" % (machine, port)
print sock.connect('tcp://%s:%s' % (machine, port))
print "Connected..."

def command_loop(socket):
    done = False
    while not done:
        command = raw_input(">")
        command = command.strip()
        if len(command) == 0:
            continue
        command = command.split()
        command, args = command[0], command[1:]

        if command == 'help':
            print "Valid commands:"
            print "  help              - display this help"
            print "  capture [x y w h] - capture a region (or entire screen)"
            print
        else:
            # TODO: expect responses
            send_command(socket, {"cmd":command, "args":args})
            print get_response(socket)
        

