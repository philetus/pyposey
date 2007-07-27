"""creates a dummy assembly event queue and sends events to test graph camera
"""

from Queue import Queue
from time import sleep

from Assembly_Graph import Assembly_Graph
from Dino_Camera import Dino_Camera

# dummy event queue and part library
queue = Queue()
library = {
    (42, 2):{"sockets":1}, # 1-socket hub
    (42, 3):{"sockets":1}, # 1-socket hub
    (42, 4):{"sockets":1}, # 1-socket hub
    (42, 5):{"sockets":1}, # 1-socket hub
    (42, 6):{"sockets":1}, # 1-socket hub
    (88, 1):{"sockets":4}, # 4-socket hub
    }

### add some events to queue

# create some hubs
queue.put( {"type":"create", "hub":(42, 2)} )
queue.put( {"type":"create", "hub":(42, 3)} )
queue.put( {"type":"create", "hub":(42, 4)} )
queue.put( {"type":"create", "hub":(88, 1)} )

# connect them
queue.put( {"type":"connect",
            "hub":(88, 1), "socket":2,
            "strut":(3, 19), "ball":0} )

queue.put( {"type":"connect",
            "hub":(42, 2), "socket":0,
            "strut":(3, 19), "ball":1} )

queue.put( {"type":"connect",
            "hub":(88, 1), "socket":0,
            "strut":(3, 20), "ball":0} )

queue.put( {"type":"connect",
            "hub":(42, 3), "socket":0,
            "strut":(3, 20), "ball":1} )

queue.put( {"type":"connect",
            "hub":(88, 1), "socket":3,
            "strut":(3, 17), "ball":0} )

queue.put( {"type":"connect",
            "hub":(42, 4), "socket":0,
            "strut":(3, 17), "ball":1} )

queue.put( {"type":"connect",
            "hub":(88, 1), "socket":1,
            "strut":(3, 18), "ball":0} )

queue.put( {"type":"configure",
            "hub":(88, 1), "socket":3,
            "roll":(90.0, 90.0),
            "pitch":(40.0, 40.0),
            "yaw":(0.0, 0.0)} )

queue.put( {"type":"configure",
            "hub":(42, 4), "socket":0,
            "roll":(0.0, 0.0),
            "pitch":(0.0, 0.0),
            "yaw":(-40.0, -40.0)} )

queue.put( {"type":"configure",
            "hub":(88, 1), "socket":1,
            "roll":(-90.0, -90.0),
            "pitch":(30.0, 30.0),
            "yaw":(0.0, 0.0)} )

queue.put( {"type":"configure",
            "hub":(88, 1), "socket":0,
            "roll":(-90.0, -90.0),
            "pitch":(-80.0, -80.0),
            "yaw":(0.0, 0.0)} )

queue.put( {"type":"configure",
            "hub":(88, 1), "socket":2,
            "roll":(-90.0, -90.0),
            "pitch":(-80.0, -80.0),
            "yaw":(0.0, 0.0)} )

queue.put( {"type":"configure",
            "hub":(42, 2), "socket":0,
            "roll":(-90.0, -90.0),
            "pitch":(-90.0, -90.0),
            "yaw":(-10.0, -10.0)} )

queue.put( {"type":"configure",
            "hub":(42, 3), "socket":0,
            "roll":(100.0, 100.0),
            "pitch":(90.0, 90.0),
            "yaw":(0.0, 0.0)} )

# create assembly graph demon with dummy queue and library
graph_demon = Assembly_Graph( event_queue=queue, part_library=library )

# create graph camera to render assembly graph
camera = Dino_Camera( graph_demon )

# start graph demon
graph_demon.start()

# show camera
camera.show()

