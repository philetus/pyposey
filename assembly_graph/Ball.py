class Ball:
    """a ball of a strut
    """

    def __init__( self, strut, index ):
        self.strut = strut
        self.index = index

        self.socket = None

    def __repr__( self ):
        return "<ball %d.%d.%d />" % ( self.strut.address + (self.index,) )
