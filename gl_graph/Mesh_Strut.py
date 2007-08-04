from pyposey.assembly_graph.Strut import Strut

from Mesh_Node import Mesh_Node

class Mesh_Strut( Strut, Mesh_Node ):
    """
    """

    def __init__( self, address, children, part_type, rootness ):
        """
        """
        Strut.__init__( self, address, children, part_type, rootness )
        self.connectors = self.balls # alias balls for mesh node
        Mesh_Node.__init__( self, address )
