class Strut_Node( object ):
    """a node representing a strut in a flexy assembly graph
    """

    class Ball( object ):
        """keeps track of which socket each ball is connected to
        """

        def __init__( self, strut, number ):
            self.strut = strut
            self.number = number

            # socket ball is connected to
            self.socket = None

            # angle and offset from parent heading and root
            if number == 0:
                self.parent_angle = 180.
                self.parent_roll = 0.
                self.parent_offset = 0.00
            else:
                self.parent_angle = 0.
                self.parent_roll = 180.
                self.parent_offset = 143.00

    def __init__( self, number ):
        self.number = number
        self.balls = []
        for i in range( 2 ):
            self.balls.append( self.Ball(self, i) )

    def connected_hubs( self ):
        """return count of hubs connected to this strut <0-2>
        """
        count = 0
        for ball in self.balls:
            if ball.socket is not None:
                count += 1

        return count

    def get_children( self ):
        """return immediate hub child nodes of this strut node
        """
        children = []
        for ball in self.balls:
            if ball.socket is not None:
                children.append( ball.socket.hub )

        return children
