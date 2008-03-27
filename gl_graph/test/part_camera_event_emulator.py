from time import sleep
import gtk
from Queue import Queue
from pyposey.assembly_graph.Part_Library import Part_Library
from pyposey.assembly_graph.Assembly_Graph import Assembly_Graph
from pyposey.gl_graph.Gimpy_Graph_Window import Gimpy_Graph_Window
from pyposey.gl_graph.Mesh_Library import Mesh_Library
from pyposey.gl_graph.Mesh_Hub import Mesh_Hub
from pyposey.gl_graph.Mesh_Strut import Mesh_Strut

# load part library
part_library = Part_Library( hub_class=Mesh_Hub, strut_class=Mesh_Strut )

# load library of part stl meshes and make dict of meshes by part type
meshes = {}
for mesh in Mesh_Library( filename="part_mesh_library.xml" ):
    meshes[mesh.part_type] = mesh

# mesh up parts
for part in part_library:
    part.set_mesh( meshes[part.type] )

# make queues
event_queue = Queue()

# build demons
assembly_graph = Assembly_Graph( event_queue=event_queue,
                                 part_library=part_library,
                                 orient=True )

# put some hardware events on sensor queue
hub0 = (42, 3)
socket0 = 0
strut0 = (3, 17)
ball0 = 0
event_queue.put( {"type":"create",
                  "hub":hub0} )
event_queue.put( {"type":"connect",
                  "hub":hub0,
                  "socket":socket0,
                  "strut":strut0,
                  "ball":ball0 } )
event_queue.put( {"type":"configure",
                  "hub":hub0,
                  "socket":socket0,
                  "strut":strut0,
                  "ball":ball0,
                  "coords":( (0, 0, 0), )} )
event_queue.put( {"type":"up",
                  "hub":hub0,
                  "x":0.5,
                  "y":0.5,
                  "z":0.5} )

# make graph window
gtk.gdk.threads_init()
gtk.gdk.threads_enter()
window = Gimpy_Graph_Window( assembly_graph )

# adjust view
window.camera.eye = ( 0, 0, -600 )
window.camera.zoom = 3.0

# start demons
assembly_graph.start()

# show window and start gtk mainloop
window.show_all()
gtk.main()
