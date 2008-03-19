from OpenGL.GL import (glPushName, glPopName, glRotatef, glMultMatrixf,
                       glPushMatrix, glPopMatrix )
from pyposey.util.Log import Log

class Mesh_Node( object ):
    """mixin to render hubs and struts with meshes in opengl
    """
    LOG = Log( name='pyposey.gl_graph.Mesh_Node', level=Log.DEBUG )

    def __init__( self, address ):
        self.gl_name = (int(self.address[0]) * 256) + int(self.address[1])
        self.mesh = None
        self.selected = False
        self.flip_count = 0

    def set_mesh( self, mesh ):
        """set opengl mesh for this node
        """
        self.mesh = mesh

        # set child transforms from mesh
        # (not implemented)

    def draw( self ):
        """call mesh to draw itself
        """
        assert self.mesh is not None
        assert self.orientation is not None

        self.LOG.debug( "drawing node %s" % str(self.address) )
        
        # push name for selection rendering pass
        glPushName( self.gl_name )
        glPushMatrix()

        # translate with node orientation matrix
        glMultMatrixf( self.orientation.gl )
        
        # rotate 90 degrees around y axis
        glRotatef( 90.0, 0.0, 1.0, 0.0 )

        # flip mesh
        flip_angle = (360 / self.mesh.flips) * self.flip_count
        glRotatef( flip_angle, *self.mesh.flip_axis )

        # call mesh to draw itself
        self.mesh.draw( selected=self.selected )

        glPopMatrix()
        glPopName()

    def flip(self):
        """rotate mesh to next possible orientation
        """
        self.flip_count = (self.flip_count + 1) % self.mesh.flips
        
