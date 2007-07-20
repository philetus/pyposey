from pyposey.util.Log import Log

class Hub_Node( object ):
    """node to represent a hub in a flexy assembly graph
    """
    LOG = Log( name='pyflexy.assembly_graph.Hub_Node', level=Log.DEBUG )

    class Socket( object ):
        """class to store socket angle and connection
        """
        DEFAULT_ANGLE = [[-180., 180.], # min, max roll
                         [-100., 100.], # min, max pitch
                         [-80., 80.]] # min, max yaw
        OFFSETS = { 1:0.00, 2:40.82, 4:60.97 }
        
        def __init__( self, hub, number, sockets ):
            self.hub = hub
            self.number = number

            # ball this socket is connected to
            self.ball = None

            # angle of strut connection
            self.angle = [[0.,0.] for i in range(3) ]
            self.reset_angle()

            # angle from parent heading
            if sockets == 1:
                self.parent_angle = 0.
            elif number == 0:
                self.parent_angle = 0.
            else:
                self.parent_angle = (-360. / sockets) * number

            # offset from parent root
            self.parent_offset = self.OFFSETS[sockets]

        def reset_angle( self ):
            for i in range( 3 ):
                for j in range( 2 ):
                    self.angle[i][j] = self.DEFAULT_ANGLE[i][j]
            
    def __init__( self, number, sockets ):
        """create a new hub with the given number of sockets
        """
        self.number = number

        # create sockets
        self.sockets = []
        for i in range( sockets ):
            self.sockets.append( self.Socket(hub=self, number=i,
                                             sockets=sockets) )

    def connect_socket( self, number, ball ):
        """connect socket of given number to given ball
        """
        socket = self.sockets[number]

        # check if either is already connected
        if socket.ball is not None:
            self.LOG.error( "socket is already connected!" )

            # disconnect from previous ball
            socket.ball.socket = None
            socket.ball = None
            
        if ball.socket is not None:
            self.LOG.error( "ball is already connected!" )

            # disconnect from previous socket
            ball.socket.ball = None
            ball.socket = None

        socket.ball = ball
        ball.socket = socket

    def disconnect_socket( self, number ):
        """disconnect socket of given number from connected ball
        """
        socket = self.sockets[number]
        if socket.ball is None:
            raise ValueError( "socket is not connected!" )
        
        socket.ball.socket = None
        socket.ball = None

        socket.reset_angle()

    def get_connected_strut( self, number ):
        """return strut connected to given socket
        """
        socket = self.sockets[number]
        if socket.ball is None:
            raise ValueError( "socket is not connected!" )
        
        return socket.ball.strut

    def set_socket_angle( self, number, roll, pitch, yaw ):
        """set angle of socket of given number
        """
        socket = self.sockets[number]
        
        if socket.ball is None:
            raise ValueError( "socket is not connected!" )

        for i, angle in enumerate( (roll, pitch, yaw) ):
            for j in range( 2 ):
                socket.angle[i][j] = angle[j]

    def get_children( self ):
        """return list of strut nodes that are immediate children of this node
        """
        children = []
        for socket in self.sockets:
            if socket.ball is not None:
                children.append( socket.ball.strut )

        return children
