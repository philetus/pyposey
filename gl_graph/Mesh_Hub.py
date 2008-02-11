from pyposey.assembly_graph.Hub import Hub

from Mesh_Node import Mesh_Node

class Mesh_Hub( Hub, Mesh_Node ):
    """hub with mesh to draw itself in opengl
    """

    def __init__( self, address, children, **args ):
        Hub.__init__( self, address, children, **args )
        Mesh_Node.__init__( self, address )
