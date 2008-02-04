from Node import Node
from Socket import Socket

class Hub( Node ):
    """a hub in a graph
    """

    def __init__( self, address, children, child_class=Socket, **args ):
        # call superclass constructor with args
        Node.__init__( self, address, children, child_class, **args )

        # hubs with accelerometers will have a vector indicating which way is
        # up set by the assembly demon
        self.up = None

    def __repr__( self ):
        return "<hub %d.%d />" % self.address

