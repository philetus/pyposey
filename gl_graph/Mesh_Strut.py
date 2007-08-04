from pyposey.assembly_graph.Strut import Strut

class Mesh_Strut( Strut ):
    """
    """

    def __init__( self, address, children, part_type, rootness ):
        """
        """
        Strut.__init__( self, address, children, part_type, rootness )

        self.mesh = None

    def set_mesh( self, mesh ):
        """
        """
        self.mesh = mesh
        for i, ball in enumerate( self.balls ):
            ball.parent_angle = mesh.parent_angles[i]
            ball.parent_offset = mesh.parent_offsets[i]

    def draw( self ):
        self.mesh.draw()
