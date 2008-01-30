from l33tC4D.vector.Polar_Vector3 import Polar_Vector3

class Map_Socket:
    """
    """
    SENSORS = [ # (lat, lon)
        (31.7, 0.0),    # 0
        (31.7, 180.0),   # 1
        (63.4, 270),   # 2
        (63.4, 90) ]   # 3

    SENSOR_RADIUS = 28.0 # 28.0 max to avoid overlap

    def __init__( self, map_ball ):
        self.map_ball = map_ball
        self.sensors = []
        for coords in self.SENSORS:
            self.sensors.append( Polar_Vector3().set_heading(*coords) )

    def get_couples( self ):
        """returns set of sensor-emitter couples
        """
        couples = set()

        for i, sensor in enumerate( self.sensors ):
            seen = set()
            for j, emitter in enumerate( self.map_ball.emitters ):

                # if angle to emitter is less than sensor radius add
                # couple to couples set
                angle = sensor.angle_to( emitter )
                #print "angle from %d, %d: %f" % ( i, j, angle )
                if self.SENSOR_RADIUS > angle:
                    couples.add( (i, j) )
                    seen.add( (j, angle) )

            if len( seen ) > 1:
                print "sensor %d sees multiple emitters: %s!" % (i, str(seen) )

        return couples
