from l33tC4D.vector.Vector3 import Vector3
from l33tC4D.vector.matrices import roll_pitch_yaw
    
class Ball( object ):
    """model of flexy ball geometry

       calculates vector from center of ball to each emitter given the current
       roll, pitch and yaw of ball
    """
    EMITTERS = [ # (lat, lon)
        (0.0, 0.0),         # 0
        (16.0, 62.3),       # 1
        (63.4, 0.0),        # 2
        (16.0, -62.3),      # 3
        (-46.4, -49.6),     # 4
        (-46.4, 49.6),      # 5
        (-16.0, 117.7),     # 6
        (-63.4, 180.0),     # 7
        (-16.0, -117.7),    # 8
        (47.7, -130.4),     # 9
        (47.7, 130.4) ]     # 10

    def __init__( self ):
        self.angle = [0, 0, 0] # roll, pitch, yaw

    def get_angle_vector( self, emitter ):
        """return 3d angle vector of given emitter's position
        """
        # create 3d vector from lat, lon of emitter
        lat, lon = self.EMITTERS[emitter]
        angle = Vector3( lat=lat, lon=lon )

        # transform angle vector by roll > pitch > yaw and return
        return angle.transform( roll_pitch_yaw(*self.angle) )
