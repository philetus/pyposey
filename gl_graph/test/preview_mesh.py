import gtk
from os import path

from Edited_Mesh_Window import Edited_Mesh_Window
from Edited_Mesh import Edited_Mesh

# load files for mesh
geometry_file = open( path.join("meshes", "bear_abdomen_c.txt"), "r" )

texture_file = open( path.join("meshes", "bear_torso_texture.png"), "rb" )

mesh = Edited_Mesh( geometry_file=geometry_file,
                    texture_file=texture_file,
                    translate=(0., 0., 0.),
                    rotate=(0., 0., 0.),
                    scale=(1.0, 1.0, 1.0) )

window = Edited_Mesh_Window( mesh, axes=True, zoom=2.0 )
window.show_all()
gtk.main()

