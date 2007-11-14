import gtk

from OpenGL.GLU import gluCylinder, gluNewQuadric

from pyposey.gl_graph.Gimpy_Camera import Gimpy_Camera

class Edited_Mesh_Window( gtk.Window ):
    """window to view edited mesh
    """

    def __init__( self, mesh, title="edited mesh window", size=(800, 600)  ):
        
        # gtk window init
        gtk.Window.__init__( self )

        self.mesh = mesh

        # set title and size
        self.set_title( title )
        self.resize( *size )

        # ???
        self.set_reallocate_redraws( True )

        # connect destroy event
        self.connect( "destroy", self._on_quit )

        # add gtk opengl draw area widget to window      
        self.camera = Gimpy_Camera()        
        self.add( self.camera )
        
        # connect camera handlers to local methods
        self.camera.handle_draw = self.handle_draw

    def handle_draw( self ):
        quadratic = gluNewQuadric()

        # draw axes
        gluCylinder( quadratic, 30.0, 10.0, 150.0, 32, 32 )

        # draw mesh
        self.mesh.draw()

    def redraw( self ):
        """add a redraw request to opengl widget event queue
        """
        self.camera.queue_draw()

    def _on_quit( self, widget ):
        self.handle_quit()
        gtk.main_quit()


if __name__ == "__main__":
    from os import path
    from Edited_Mesh import Edited_Mesh

    # load files for mesh
    geometry_file = open(
        path.join("meshes", "bearx_mesh_5.txt"),
        "r" )
    texture_file = open(
        path.join("meshes", "bearx_head_texture.jpg"),
        "rb" )
    thumbnail_file = open(
        path.join("meshes", "bear_head_thumbnail.png"),
        "rb" )

    mesh = Edited_Mesh( name="test",
                        part_type="one_hub",
                        geometry_file=geometry_file,
                        texture_file=texture_file,
                        thumbnail_file=thumbnail_file,
                        parent_angles=(0., 0., 0.),
                        parent_offsets=0.,
                        translate=(0., 0., 0.),
                        rotate=(0., 0., 0.),
                        scale=(1.0, 1.0, 1.0) )
    
    window = Edited_Mesh_Window( mesh )
    window.show_all()
    gtk.main()

