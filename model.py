import argparse
import json
import re
import sys

# A Model is just an array of input messages and actions.
#
# Attributes for each action include:
# send: <another message>
# report: <report something>

ACTIONS = ['send', 'report', "tstart", "tstop"]

QUEUE = []
TIME = 0
OUT = None

LEFT_COLUMN = 1
RIGHT_COLUMN = 5
TIME_SCALE = -1.3

def get_latency(m):
    global args
    
    if m == "START":
        return 0
    if m.startswith("offer") or m.startswith("answer"):
        return args.signaling
    return .5

def voffset(t):
    return t * TIME_SCALE

def queue(t, a, m):
    QUEUE.append([t, t + get_latency(m), a, m])
    QUEUE.sort(key = lambda x: x[0])

def message_key(m):
    return m.split(":")[0]

def message_txt(m):
    return m.split(":")[-1]    

def draw_arrow(source, send_time, receive_time, message):
    if source.name_ == "answerer":
        start_time = send_time
        end_time = receive_time
        align = "aligned above"
        arrow = "->"
    else:
        start_time = receive_time
        end_time = send_time
        align = "aligned above"
        arrow = "<-"
        
    OUT.write("arrow %s \"%s\" %s from %f,%f to %f,%f\n"
              %(arrow, message_txt(message), align, LEFT_COLUMN, voffset(start_time), RIGHT_COLUMN, voffset(end_time)))

def draw_timepoint(agent, label, start_time, end_time):
    if agent == "offerer":
        x = LEFT_COLUMN - .1
    else:
        x = RIGHT_COLUMN + .1

    OUT.write("arrow \"%.3g RTT\" from %f, %f to %f, %f\n"
              %(end_time - start_time, x, voffset(start_time), x, voffset(end_time)))
        
class Model:
    def __init__(self, name, machine):
        self.name_ = name
        self.machine_ = []
        for k in machine:
            mach = {}
            for a in ACTIONS:
                mach[a] = []
                if a in machine[k]:
                    mach[a] = machine[k][a]
            self.machine_.append([k, mach])
        self.queue_ = []
        self.received_ = []
        self.timepoints_ ={}

    def set_peer(self, p):
        self.peer_ = p
        
    def trace_in(self, m):
        print "%f: %s: IN %s "%(TIME, self.name_, m)
        
    def trace_out(self, m):
        print "%f: %s: OUT %s "%(TIME, self.name_, m)
        
    def report(self, m):
        print "%f: %s: ACTION %s"%(TIME, self.name_, m)
        
    def incoming(self, message):
        global args
        self.trace_in(message)
        message = message_key(message)
        for i in range(0, len(self.machine_)):
            pair = self.machine_[i]
            k = pair[0]
            m = pair[1]
            if k == message:
                for r in m['report']:
                    self.report(r)
                t = TIME
                for s in m['send']:
                    self.trace_out(s)
                    queue(t, self.peer_, s)
                    t += args.message_offset
                for s in m['tstart']:
                    self.timepoints_[s] = TIME
                for s in m['tstop']:
                    draw_timepoint(self.name_, s, self.timepoints_[s], TIME)
                    del self.timepoints_[s]
                
            elif k.find("|") != -1:
                messages = k.split("|")
                if message in messages:
                    # Take ourselves off the list
                    self.machine_.pop(i)
                    messages.remove(message)
                    self.machine_.append(["|".join(messages), pair[1]])



parser = argparse.ArgumentParser(description="Ladder diagrams from simple models")
parser.add_argument('--signaling', dest="signaling", type=float, default=0.7,
                    help="delivery time for signaling messages")
parser.add_argument('--moffset', dest="message_offset", type=float, default=0.02,
                    help="inter-message time")
parser.add_argument('file')
args = parser.parse_args()

j = open(args.file, "r")
model = json.load(j)
OUT = open(re.sub("\.json$",".pic",args.file), "w")

offerer = Model("offerer", model["offerer"])
answerer = Model("answerer", model["answerer"])

offerer.set_peer(answerer)
answerer.set_peer(offerer)

queue(0, offerer, "START")
OUT.write(".PS\n")

while(len(QUEUE)):
    m = QUEUE.pop(0)
    TIME = m[1]
    m[2].incoming(m[3])
    if m[3] != "START":
        draw_arrow(m[2], m[0], m[1], m[3])

OUT.write(".PE")



        



