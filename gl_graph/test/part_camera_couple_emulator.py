import gtk
from Queue import Queue
from pyposey.hardware_demon.Assembly_Demon import Assembly_Demon
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
sensor_queue = Queue()
event_queue = Queue()

# build demons
assembly_demon = Assembly_Demon( sensor_queue, event_queue )
assembly_graph = Assembly_Graph( event_queue=event_queue,
                                 part_library=part_library,
                                 orient=True )


HUB = (42, 2, 0)
STRUT = (3, 17, 0)
def put_couple( sensor, emitter ):
    strut_address = STRUT[:2]
    if emitter == None:
        strut_address = (0, 0)
    sensor_queue.put( {"type":"couple",
                       "hub_address":HUB[:2],
                       "socket_index":HUB[2],
                       "sensor_index":sensor,
                       "strut_address":strut_address,
                       "ball_index":STRUT[2],
                       "emitter_index":emitter} )

# put some hardware events on sensor queue
put_couple( 0, 0 )
put_couple( 1, 0 )

# make graph window
gtk.gdk.threads_init()
gtk.gdk.threads_enter()
window = Gimpy_Graph_Window( assembly_graph )

# adjust view
window.camera.eye = ( 0, 0, -600 )
window.camera.zoom = 3.0

# start demons
assembly_demon.start()
assembly_graph.start()

# show window and start gtk mainloop
window.show_all()
gtk.main()
