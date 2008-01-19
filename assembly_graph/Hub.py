from Socket import Socket

class Hub:
    """a hub in a graph
    """

    def __init__( self, address, children, part_type, rootness, label):
        self.address = address
        self.rootness = rootness
        self.label = label
        self.type = part_type
        self.subgraph = None

        # hubs with accelerometers will have a vector indicating which way is
        # up set by the assembly demon
        self.up = None

        # add sockets to sockets list
        self.sockets = []
        for i in range( children ):
            socket = Socket( hub=self,
                             index=i )
            self.sockets.append( socket )

    def __repr__( self ):
        return "<hub %d.%d />" % self.address

    def __getitem__( self, key ):
        return self.sockets[key]

    def __iter__( self ):
        for socket in self.sockets:
            yield socket

    def __len__( self ):
        return len( self.sockets )

    def get_connected( self ):
        """returns set of struts connected to this hub
        """
        connected = set()
        for socket in self.sockets:
            if socket.ball is not None:
                connected.add( socket.ball.strut )
                
        return connected
