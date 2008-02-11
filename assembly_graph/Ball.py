from l33tC4D.vector.Matrix3 import Matrix3
from Child import Child

class Ball( Child ):
    """a ball of a strut
    """

    def __init__( self, parent, index, transform=None ):
        Child.__init__( self, parent, index, transform )
        
        self.out_transform = self._transform
        self.build_transforms()
        
    def __repr__( self ):
        return "<ball %d.%d.%d />" % ( self.parent.address + (self.index,) )

    def build_transforms( self ):
        """builf matrix to transform from child to parent
        """
        if self._transform is None:
            self.in_transform = None
            return

        # start with out transform
        transform = Matrix3( self._transform )

        # rotate 180 degrees around x axis to flip z direction to face in
        transform.rotate( 180, self.X )

        # invert to come back from there
        transform.invert()

        self.in_transform = transform

