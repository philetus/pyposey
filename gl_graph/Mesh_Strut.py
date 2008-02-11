from pyposey.assembly_graph.Strut import Strut

from Mesh_Node import Mesh_Node

class Mesh_Strut( Strut, Mesh_Node ):
    """strut with mesh to draw itself in opengl
    """

    def __init__( self, address, children, **args ):
        Strut.__init__( self, address, children, **args )
        Mesh_Node.__init__( self, address )
