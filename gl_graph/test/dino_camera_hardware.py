import gtk
from Queue import Queue

from pyposey.hardware_demon.Sensor_Demon import Sensor_Demon
from pyposey.hardware_demon.Assembly_Demon import Assembly_Demon
from pyposey.assembly_graph.Part_Library import Part_Library

from pyposey.gl_graph.Gimpy_Graph_Window import Gimpy_Graph_Window
from pyposey.gl_graph.Mesh_Library import Mesh_Library
from pyposey.gl_graph.Mesh_Hub import Mesh_Hub
from pyposey.gl_graph.Mesh_Strut import Mesh_Strut

# make fake event queue
queue = Queue()

# load part library
part_library = Part_Library( hub_class=Mesh_Hub, strut_class=Mesh_Strut )

# load library of part stl meshes
meshes = Mesh_Library( filename="dinosaur_mesh_library.xml" )

# mesh up parts
part_library[(88, 1)].set_mesh( meshes["dinosaur body"] )
part_library[(42, 3)].set_mesh( meshes["dinosaur head"] )
part_library[(3, 17)].set_mesh( meshes["dinosaur neck"] )

# set up assembly demon
sensor_queue = Queue()
assembly_queue = Queue()

sensor_demon = Sensor_Demon( sensor_queue, serial_port="/dev/ttyUSB0" )
assembly_demon = Assembly_Demon( sensor_queue, assembly_queue )
sensor_demon.start()
assembly_demon.start()

# make graph window
gtk.gdk.threads_init()
gtk.gdk.threads_enter()
window = Gimpy_Graph_Window( part_library=part_library,
                             event_queue=assembly_queue )

# adjust view
window.camera.eye = ( 0, 0, -600 )
window.camera.zoom = 3.0

# show window and start gtk mainloop
window.show_all()
gtk.main()
