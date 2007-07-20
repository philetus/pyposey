from l33tC4D.vector.Vector3 import Vector3

class Socket( object ):
    """model of flexy socket geometry

       calclulates set of couples visible from current ball angle
    """
    SENSORS = [ # (lat, lon)
        (31.7, 0.0),    # 0
        (-31.7, 0.0),   # 1
        (0.0, -63.4),   # 2
        (0.0, 63.4) ]   # 3

    SENSOR_RADIUS = 30.0

    def __init__( self, ball ):
        self.ball = ball

    def get_couples( self ):
        """returns set of sensor-emitter couples
        """
        couples = set()

        # get lat, lon vector for each emitter
        for emitter in range(len( self.ball.EMITTERS) ):
            emitter_vector = self.ball.get_angle_vector( emitter )

            # get lat, lon vector for each sensor
            for sensor in range( len(self.SENSORS) ):
                lat, lon = self.SENSORS[sensor]
                sensor_vector = Vector3( lat=lat, lon=lon )

                # if angle to emitter is less than sensor radius add
                # couple to couples set
                angle = emitter_vector.angle_to( sensor_vector )
                if angle < self.SENSOR_RADIUS:
                    couples.add( (sensor, emitter) )

        return couples

