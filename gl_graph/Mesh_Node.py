from OpenGL.GL import glPushName, glPopName, glRotate, glPushMatrix, glPopMatrix

class Mesh_Node( object ):
    """mixin to render hubs and struts with meshes in opengl
    """

    def __init__( self, address ):
        """
        """
        self.gl_name = (int(self.address[0]) * 256) + int(self.address[1])
        self.mesh = None
        self.selected = False
        self.flip_count = 0

    def set_mesh( self, mesh ):
        """
        """
        self.mesh = mesh
        for i, connector in enumerate( self.connectors ):
            connector.parent_angle = mesh.parent_angles[i]
            connector.parent_offset = mesh.parent_offsets[i]

    def draw( self ):
        # push name for selection rendering pass
        glPushName( self.gl_name )
        glPushMatrix()

        # flip mesh
        flip_angle = (360 / self.mesh.flips) * self.flip_count
        glRotate( flip_angle, *self.mesh.flip_axis )

        # call mesh to draw itself
        self.mesh.draw( selected=self.selected )

        glPopMatrix()
        glPopName()

    def flip(self):
        self.flip_count = (self.flip_count + 1) % self.mesh.flips
        
