from l33tC4D.vector.Polar_Vector3 import Polar_Vector3

class Map_Ball:
    """model of the position of the emitters on a posey ball
    """
    EMITTERS = [ # (lat, lon)
        (0.0, 0.0),         # 0
        (63.4, 72.0),       # 1
        (63.4, 0.0),        # 2
        (63.4, 288.0),      # 3
        (63.4, 216.0),      # 4
        (63.4, 144.0),      # 5
        (126.8, 108.0),     # 6
        (126.8, 180.0),     # 7
        (126.8, 252.0),     # 8
        (126.8, 324.0),     # 9
        (126.8, 36.0) ]     # 10

    def __init__( self ):
        """
        """
        self.emitters = []
        for i in range( len(self.EMITTERS) ):
            self.emitters.append( Polar_Vector3() )
        self.reset()

    def reset( self ):
        """reset emitter vectors to original positions
        """
        for emitter, coords in zip( self.emitters, self.EMITTERS ):
            emitter.set_heading( *coords )

    def transform( self, matrix3 ):
        """transform ball with given matrix
        """
        for emitter in self.emitters:
            emitter.transform( matrix3 )
        
