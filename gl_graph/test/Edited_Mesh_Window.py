import gtk

from OpenGL.GL import glTranslate, glRotate, glPushMatrix, glPopMatrix
from OpenGL.GLU import gluCylinder, gluNewQuadric

from pyposey.gl_graph.Gimpy_Camera import Gimpy_Camera

class Edited_Mesh_Window( gtk.Window ):
    """window to view edited mesh
    """

    def __init__( self, mesh, title="edited mesh window", size=(800, 600),
                  axes=True, zoom=3.0 ):
        
        # gtk window init
        gtk.Window.__init__( self )

        self.mesh = mesh
        self.axes = axes

        # set title and size
        self.set_title( title )
        self.resize( *size )

        # ???
        self.set_reallocate_redraws( True )

        # add gtk opengl draw area widget to window      
        self.camera = Gimpy_Camera()        
        self.add( self.camera )

        self.camera.zoom = zoom

        # connect events
        self.connect( "destroy", self._on_quit )
        
        # connect camera handlers to local methods
        self.camera.handle_draw = self.handle_draw

        print "finished init"

    def handle_draw( self ):
        #print "drawing ...",
        try:
            
            # draw axes
            if self.axes:
                glPushMatrix()
                quadratic = gluNewQuadric()

                # long cone is default axis
                gluCylinder( quadratic, 30.0, 10.0, 140.0, 32, 32 )

                # short cone rotated 90 degrees
                glTranslate( 30.0, 0.0, 0.0 )
                glRotate( 90.0, 1.0, 0.0, 0.0 )
                gluCylinder( quadratic, 30.0, 10.0, 71.5, 32, 32 )

                #glRotate( -90.0, 0.0, 1.0, 0.0 )
                #glRotate( -90.0, 0.0, 1.0, 0.0 )
                #gluCylinder( quadratic, 30.0, 10.0, 71.5, 32, 32 )
                #glRotate( -90.0, 0.0, 1.0, 0.0 )
                glPopMatrix()
            
            # draw mesh
            self.mesh.draw()

        except Exception, error:
            print "failed to draw:", str(error)

        #print "done drawing"

    def redraw( self ):
        """add a redraw request to opengl widget event queue
        """
        self.camera.queue_draw()

    def _on_quit( self, widget ):
        #self.handle_quit()
        gtk.main_quit()


