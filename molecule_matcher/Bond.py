from Atom_Set import Atom_Set

class Bond( object ):
    """a edge in a graph of bonded atoms
    """

    def __init__( self, address=None ):
        self.address = address
        self.atom_set = Atom_Set()

    def __repr__( self ):
        return '<bond address="%s" />' % ".".join(
            [str(i) for i in self.address] )
    
