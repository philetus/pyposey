from l33tC4D.vector.Matrix3 import Matrix3
from l33tC4D.vector.Vector3 import Vector3

class Child:
    """superclass for ball and socket node connectors
    """
    X = Vector3( (1, 0, 0) ) # x-axis vector
    
    def __init__( self, parent, index, transform=None ):
        self.parent = parent
        self.index = index
        self.connected = None
        self._transform = ( Matrix3( transform ) if transform is not None
                                else None )

        # children are responsible for maintaining transformation matrices
        # in and out of parent orientation
        self.in_transform = None
        self.out_transform = None

    def _get_address( self ):
        return self.parent.address + (self.index, )
    
    address = property( fget=_get_address )
