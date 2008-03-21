import gtk
from os import path

from Edited_Mesh_Window import Edited_Mesh_Window
from pyposey.gl_graph.STL_Mesh import STL_Mesh

# load files for mesh
stl_file = open( path.join("meshes", "graphics_one_hub.stl"), "r" )

thumbnail_file = open( path.join("meshes", "graphics_four_hub_thumbnail.png"), "rb" )

mesh = STL_Mesh( name="test",
                 part_type="test",
                 stl_file=stl_file,
                 thumbnail_file=thumbnail_file,
                 specular=(1.0, 1.0, 1.0, 1.0),
                 shininess=20.0,
                 diffuse=(0.0, 0.7, 0.1, 1.0),
                 parent_angles=(0.0, 0.0, 0.0),
                 parent_offsets=0.0 )

print mesh

window = Edited_Mesh_Window( mesh, axes=True, zoom=1.0 )
window.show_all()
gtk.main()

