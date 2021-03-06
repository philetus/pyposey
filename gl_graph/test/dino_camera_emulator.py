import gtk
from Queue import Queue

from pyposey.assembly_graph.Part_Library import Part_Library

from pyposey.gl_graph.Gimpy_Graph_Window import Gimpy_Graph_Window
from pyposey.gl_graph.Mesh_Library import Mesh_Library
from pyposey.gl_graph.Mesh_Hub import Mesh_Hub
from pyposey.gl_graph.Mesh_Strut import Mesh_Strut

# make fake event queue
queue = Queue()

# put some events on queue
# create some hubs
queue.put( {"type":"create", "hub":(42, 3)} )
queue.put( {"type":"create", "hub":(88, 1)} )

# connect them
queue.put( {"type":"connect",
            "hub":(42, 3), "socket":0,
            "strut":(3, 17), "ball":0} )
queue.put( {"type":"connect",
            "hub":(88, 1), "socket":1,
            "strut":(3, 17), "ball":1} )


# change the socket angles
queue.put( {"type":"configure",
            "hub":(42, 3), "socket":0,
            "roll":(0.0, 0.0),
            "pitch":(0.0, 0.0),
            "yaw":(0.0, 0.0)} )
queue.put( {"type":"configure",
            "hub":(88, 1), "socket":0,
            "roll":(90.0, 90.0),
            "pitch":(60.0, 60.0),
            "yaw":(0.0, 0.0)} )

# load part library
part_library = Part_Library( hub_class=Mesh_Hub, strut_class=Mesh_Strut )

# load library of part stl meshes
meshes = Mesh_Library( filename="dinosaur_mesh_library.xml" )

# mesh up parts
part_library[(88, 1)].set_mesh( meshes["dinosaur body"] )
part_library[(42, 3)].set_mesh( meshes["dinosaur head"] )
part_library[(3, 17)].set_mesh( meshes["dinosaur neck"] )

# make graph window
window = Gimpy_Graph_Window( part_library=part_library, event_queue=queue )

# adjust view
window.camera.eye = ( 0, 0, -600 )
window.camera.zoom = 3.0

# show window and start gtk mainloop
window.show_all()
gtk.main()
