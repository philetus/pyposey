from pyposey.util.Log import Log

class Socket:
    """a socket of a hub
    """

    LOG = Log( name='pyposey.assembly_graph.Socket', level=Log.WARN )

    DEFAULT_ANGLE = [ 0.0, 0.0, 0.0 ]
    
    def __init__( self, hub, index ):
        self.hub = hub
        self.index = index

        # distance to parent centroid
        self.parent_angle = None
        self.parent_offset = None

        # ball this socket is connected to
        self.ball = None

        # angle of strut connection
        self.angle = None
        self.reset_angle()

    def __repr__( self ):
        return "<socket %d.%d.%d />" % ( self.hub.address + (self.index,) )

    def reset_angle( self ):
        """reset angle to default angle
        """
        self.angle = list( self.DEFAULT_ANGLE )

    def connect( self, ball ):
        """connect this socket to given ball
        """
        # make sure ball and socket are disconnected
        assert self.ball is None
        assert ball.socket is None

        self.ball = ball
        ball.socket = self

    def disconnect( self ):
        """
        """
        if self.ball is None:
            self.LOG.error( "disconnecting but socket not connected!" )
        self.ball.socket = None
        self.ball = None

    def set_angle( self, roll, pitch, yaw ):
        for i, pair in enumerate([ roll, pitch, yaw ]):
            self.angle[i] = sum( pair ) / 2.0
