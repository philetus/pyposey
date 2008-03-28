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
        return "<ball %d.%d.%d />" % self.address

    def build_transforms( self ):
        """build matrix to transform from child to parent
        """
        if self._transform is None:
            self.in_transform = None
            return

        # create transform
        transform = Matrix3()

        # rotate 180 degrees around x axis to face in
        transform.rotate( 180, self.X )

        # apply inverted out transform to return to origin
        transform.transform( Matrix3(self._transform).invert() )

        self.in_transform = transform

