from Node import Node
from Ball import Ball

class Strut( Node ):
    """represents strut in assembly graph
    """
    
    def __init__( self, address, children, child_class=Ball, **args ):
        # call superclass constructor with args
        Node.__init__( self, address, children, child_class, **args )

    def __repr__( self ):
        return "<strut %d.%d />" % self.address
