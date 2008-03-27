from l33tC4D.vector.Polar_Vector3 import Polar_Vector3

class Map_Socket:
    """
    """
    SENSORS = [ # (lat, lon)
        (31.7, 180.0),      # 0
        (31.7, 0.0),        # 1
        (63.4, 270.0),      # 2
        (63.4, 90.0) ]      # 3

    SENSOR_RADIUS = 30.0 # 31.6 max to avoid overlap

    def __init__( self, map_ball ):
        self.map_ball = map_ball
        self.sensors = []
        for coords in self.SENSORS:
            self.sensors.append( Polar_Vector3().set_heading(*coords) )

    def get_couples( self ):
        """returns set of sensor-emitter couples
        """
        couples = set()
        
        emitters = [ [] for i in range(len(self.map_ball.emitters)) ]
        
        for i, sensor in enumerate( self.sensors ):
            seen = set()
            for j, emitter in enumerate( self.map_ball.emitters ):

                # if angle to emitter is less than sensor radius add
                # couple to couples set
                angle = sensor.angle_to( emitter )
                
                #if i == 0 and j == 0:
                #    print "angle from %d, %d: %f" % ( i, j, angle )
                #    print "(%.2f)" % angle,
                
                if self.SENSOR_RADIUS > angle:
                    couples.add( (i, j) )
                    seen.add( (j, angle) )
                    emitters[j].append( i )

##            if len( seen ) > 1:
##                print "sensor %d sees multiple emitters: %s!" % (i, str(seen) )
##
##        for i, l in enumerate( emitters ):
##            if len( l ) > 1:
##                print "emitter %d sees multiple sensors: %s!" % (i, str(l) )
                
        return couples

    def test_distances( self ):
        for i in range(len(self.sensors)):
            for j in range(len(self.sensors)):
                if i < j:
                    angle = self.sensors[i].angle_to( self.sensors[j] )
                    print "angle from sensor %d to sensor %d: %.1f" % (
                        i, j, angle)
