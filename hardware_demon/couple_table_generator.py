from Vector import Vector

class Ball( object ):
    """
    """

    EMITTERS = [ # (lat, lon)
        (0.0, 0.0), # 0
        (0.0, 63.0), # 1
        (62.3, 31.7), # 2
        (49.6, -58.3), # 3
        (-49.6, -58.3), # 4
        (-62.3, 31.7), # 5
        (-130.4, 121.7), # 6
        (130.4, 121.7), # 7
        (117.7, -148.3), # 8
        (0.0, -116.6), # 9
        (-117.7, -148.3) ] # 10
    
    def __init__( self ):
        self.angle = [0, 0, 0] # roll, pitch, yaw

    def emitter_angle( self, emitter ):
        """return (latitude, longitude) of given emitter
        """
        # get latitude, longitude of emitter
        latlon = Vector( *self.EMITTERS[emitter] )

        # adjust latitude and longitude for roll
        latlon.rotate( self.angle[0] )

        # return latitude and longitude adjusted for pitch and yaw
        return latlon[0] + self.angle[1], latlon[1] + self.angle[2]
        
        
