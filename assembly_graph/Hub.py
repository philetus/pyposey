from Socket import Socket

class Hub:
    """a hub in a graph
    """

    def __init__( self, address, children, part_type, rootness ):
        self.address = address
        self.rootness = rootness
        self.type = part_type
        self.subgraph = None

        # add sockets to sockets list
        self.sockets = []
        for i in range( children ):
            socket = Socket( hub=self,
                             index=i )
            self.sockets.append( socket )

    def __getitem__( self, key ):
        return self.sockets[key]

    def __iter__( self ):
        return self.sockets.itervalues()

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