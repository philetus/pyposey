from OpenGL.GL import glPushName, glPopName

class Mesh_Node( object ):
    """mixin to render hubs and struts with meshes in opengl
    """

    def __init__( self, address ):
        """
        """
        self.gl_name = (int(self.address[0]) * 256) + int(self.address[1])
        self.mesh = None
        self.selected = False
        self.flip = -1

    def set_mesh( self, mesh ):
        """
        """
        self.mesh = mesh
        for i, connector in enumerate( self.connectors ):
            connector.parent_angle = mesh.parent_angles[i]
            connector.parent_offset = mesh.parent_offsets[i]

    def draw( self ):
        glPushName( self.gl_name )
        self.mesh.draw( selected=self.selected, flip=self.flip )
        glPopName()

    def inc_flip(self):
        self.flip = (self.flip+1) % 4
        
