from pyposey.assembly_graph.Hub import Hub

class Mesh_Hub( Hub ):
    """
    """

    def __init__( self, address, children, part_type, rootness ):
        """
        """
        Hub.__init__( self, address, children, part_type, rootness )

        self.mesh = None

    def set_mesh( self, mesh ):
        """
        """
        self.mesh = mesh
        for i, socket in enumerate( self.sockets ):
            socket.parent_angle = mesh.parent_angles[i]
            socket.parent_offset = mesh.parent_offsets[i]

    def draw( self ):
        self.mesh.draw()
