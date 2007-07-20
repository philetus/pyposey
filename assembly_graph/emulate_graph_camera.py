"""creates a dummy assembly event queue and sends events to test graph camera
"""

from Queue import Queue
from time import sleep
from threading import Thread

from Assembly_Graph import Assembly_Graph
from Graph_Camera import Graph_Camera

class Invisible_Hand( Thread ):
    
    def __init__( self, queue ):
        Thread.__init__( self )
        self.queue = queue
        self.roll = 0.0
        self.pitch = 0.0
        self.yaw = 0.0
        
    def run( self ):
        pitch_dir = 1.0
        while self.queue is not None:
            sleep( 0.5 )
            
            self.roll += 15.0
            if self.roll > 180.0:
                self.roll = -180.0
                
            self.pitch += 15.0 * pitch_dir
            if self.pitch > 100.0:
                pitch_dir = -1.0
            elif self.pitch < -100.0:
                pitch_dir = 1.0

            self.queue.put( {"type":"configure",
                             "hub":(42, 3), "socket":0,
                             "roll":(0.0, 0.0),
                             "pitch":(self.pitch, self.pitch),
                             "yaw":(90.0, 90.0)} )
##            self.queue.put( {"type":"configure",
##                             "hub":(42, 4), "socket":0,
##                             "roll":(30.0, 30.0),
##                             "pitch":(self.pitch, self.pitch),
##                             "yaw":(90.0, 90.0)} )
            

# dummy event queue and part library
queue = Queue()
library = {
    (88, 1):{"sockets":4}, # 4-socket hub
    (42, 3):{"sockets":1}, # 1-socket hub
    (42, 4):{"sockets":1}, # 1-socket hub
    (42, 5):{"sockets":1}, # 1-socket hub
    }

### add some events to queue

# create some hubs
queue.put( {"type":"create", "hub":(42, 3)} )
queue.put( {"type":"create", "hub":(42, 4)} )

# connect them
queue.put( {"type":"connect",
            "hub":(42, 3), "socket":0,
            "strut":(3, 17), "ball":0} )
queue.put( {"type":"connect",
            "hub":(42, 4), "socket":0,
            "strut":(3, 17), "ball":1} )


# change the socket angles
##queue.put( {"type":"configure",
##            "hub":(42, 3), "socket":0,
##            "roll":(0.0, 0.0),
##            "pitch":(0.0, 0.0),
##            "yaw":(0.0, 0.0)} )
##queue.put( {"type":"configure",
##            "hub":(42, 4), "socket":0,
##            "roll":(90.0, 90.0),
##            "pitch":(60.0, 60.0),
##            "yaw":(0.0, 0.0)} )

# create assembly graph demon with dummy queue and library
graph_demon = Assembly_Graph( event_queue=queue, part_library=library )

# create graph camera to render assembly graph
camera = Graph_Camera( graph_demon )
camera.eye = ( 0.0, 0.0, -2000.0 )

# start graph demon
graph_demon.start()

# start invisible hand
hand = Invisible_Hand( queue )
##hand.start()

# show camera
camera.show()

