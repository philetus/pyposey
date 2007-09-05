from pyposey.assembly_graph.Strut import Strut

from Mesh_Node import Mesh_Node

class Mesh_Strut( Strut, Mesh_Node ):
    """
    """

    def __init__( self, address, children, part_type, rootness, label="x" ):
        """
        """
        Strut.__init__( self, address, children, part_type, rootness, label )
        self.connectors = self.balls # alias balls for mesh node
        Mesh_Node.__init__( self, address )
