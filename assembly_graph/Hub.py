from l33tC4D.vector.Vector3 import Vector3
from pyposey.util.Log import Log
from Node import Node
from Socket import Socket

class Hub( Node ):
    """a hub in a graph
    """
    LOG = Log( name='pyposey.assembly_graph.Hub', level=Log.INFO)
    
    def __init__( self, address, children, child_class=Socket, **args ):
        # call superclass constructor with args
        Node.__init__( self, address, children, child_class, **args )

        # hubs with accelerometers will have a vector indicating which way is
        # up set by the assembly demon
        self.up = None

    def __repr__( self ):
        return "<hub %d.%d />" % self.address

    def set_up( self, x, y, z ):
        """set hub up vector
        """
        self.up = Vector3( (x, y, z) )

        self.LOG.info( "new up vector for %s: %s" % (str(self), str(self.up)) )
        
