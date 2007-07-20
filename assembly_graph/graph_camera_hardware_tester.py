"""sets up sensor demon and assembly demon to feed graph camera
"""

from Queue import Queue
from time import sleep

from pyposey.hardware_demon.Sensor_Demon import Sensor_Demon
from pyposey.hardware_demon.Assembly_Demon import Assembly_Demon

from Assembly_Graph import Assembly_Graph
from Graph_Camera import Graph_Camera

# part library
library = {
    (42, 2):{"sockets":1}, # 1-socket hub
    (42, 3):{"sockets":1}, # 1-socket hub
    (42, 4):{"sockets":1}, # 1-socket hub
    (42, 5):{"sockets":1}, # 1-socket hub
    (42, 6):{"sockets":1}, # 1-socket hub
    (88, 1):{"sockets":4}, # 4-socket hub
    }

# create event queues
sensor_queue = Queue()
assembly_queue = Queue()

# create hardware demons to manage event queues
sensor_demon = Sensor_Demon( sensor_queue=sensor_queue )

assembly_demon = Assembly_Demon( sensor_queue=sensor_queue,
                        assembly_queue=assembly_queue )

# create assembly graph demon with assembly queue and library
graph_demon = Assembly_Graph( event_queue=assembly_queue, part_library=library )

# create graph camera to render assembly graph
camera = Graph_Camera( graph_demon )

# start demons
sensor_demon.start()
assembly_demon.start()
graph_demon.start()

# show camera
camera.show()

