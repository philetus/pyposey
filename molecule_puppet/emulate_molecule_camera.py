"""creates a dummy assembly event queue and sends events to test graph camera
"""

from Queue import Queue
from time import sleep

from Assembly_Graph import Assembly_Graph
from Molecule_Camera import Molecule_Camera

# dummy event queue and part library
queue = Queue()
library = {
    (42, 1):{"sockets":1}, # hydrogen
    (42, 2):{"sockets":1}, # hydrogen
    (88, 1):{"sockets":4}, # carbon
    (88, 2):{"sockets":4}, # carbon
    }

### add some events to queue

# create some hubs
queue.put( {"type":"create", "hub":(88,1)} )

# add first bond
queue.put( {"type":"connect",
            "hub":(88,1), "socket":0,
            "strut":(17, 1), "ball":0} )

queue.put( {"type":"configure",
            "hub":(88, 1), "socket":0,
            "roll":(0., 0.),
            "pitch":(90., 90.),
            "yaw":(0., 0)} )

# add second bond
queue.put( {"type":"connect",
            "hub":(88,1), "socket":1,
            "strut":(17, 2), "ball":0} )

queue.put( {"type":"configure",
            "hub":(88, 1), "socket":1,
            "roll":(0., 0.),
            "pitch":(90., 90.),
            "yaw":(0., 0)} )

# add a carbon
queue.put( {"type":"create", "hub":(88,2)} )
queue.put( {"type":"connect",
            "hub":(88,2), "socket":0,
            "strut":(17, 1), "ball":1} )

queue.put( {"type":"connect",
            "hub":(88,1), "socket":2,
            "strut":(17, 3), "ball":0} )

queue.put( {"type":"configure",
            "hub":(88, 1), "socket":2,
            "roll":(0., 0.),
            "pitch":(90., 90.),
            "yaw":(0., 0)} )

queue.put( {"type":"configure",
            "hub":(88, 2), "socket":0,
            "roll":(0., 0.),
            "pitch":(90., 90.),
            "yaw":(0., 0)} )

# add a hydrogen
queue.put( {"type":"connect",
            "hub":(88,1), "socket":3,
            "strut":(17, 4), "ball":0} )

queue.put( {"type":"configure",
            "hub":(88, 1), "socket":3,
            "roll":(0., 0.),
            "pitch":(-80., -80.),
            "yaw":(0., 0)} )

queue.put( {"type":"create", "hub":(42,1)} )

queue.put( {"type":"connect",
            "hub":(42,1), "socket":0,
            "strut":(17, 4), "ball":1} )

# add another hydrogen
queue.put( {"type":"connect",
            "hub":(88,2), "socket":1,
            "strut":(17, 5), "ball":0} )

queue.put( {"type":"configure",
            "hub":(88, 2), "socket":1,
            "roll":(0., 0.),
            "pitch":(-85., -85.),
            "yaw":(0., 0)} )

queue.put( {"type":"create", "hub":(42,2)} )

queue.put( {"type":"connect",
            "hub":(42,2), "socket":0,
            "strut":(17, 5), "ball":1} )



# create assembly graph demon with dummy queue and library
graph_demon = Assembly_Graph( event_queue=queue, part_library=library )

# create graph camera to render assembly graph
camera = Molecule_Camera( graph_demon )

# start graph demon
graph_demon.start()

# show camera
camera.show()

