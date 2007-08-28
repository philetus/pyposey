from Ball import Ball

class Strut:
    """represents strut in assembly graph
    """
    
    def __init__( self, address, children, part_type, rootness, label ):
        self.address = address
        self.rootness = rootness
        self.label = label
        self.type = part_type
        self.subgraph = None

        # create balls
        self.balls = []
        for i in range( children ):
            ball = Ball( strut=self,
                         index=i )
            self.balls.append( ball )

    def __getitem__( self, key ):
        return self.balls[key]

    def __iter__( self ):
        return self.balls.itervalues()

    def get_connected( self ):
        """returns set of hubs connected to this strut
        """
        connected = set()
        for ball in self.balls:
            if ball.socket is not None:
                connected.add( ball.socket.hub )

        return connected
    
