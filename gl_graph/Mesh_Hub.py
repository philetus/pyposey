from pyposey.assembly_graph.Hub import Hub

from Mesh_Node import Mesh_Node

class Mesh_Hub( Hub, Mesh_Node ):
    """
    """

    def __init__( self, address, children, part_type, rootness, label="x" ):
        """
        """
        Hub.__init__( self, address, children, part_type, rootness, label )
        self.connectors = self.sockets # alias sockets for mesh node
        Mesh_Node.__init__( self, address )
