from Vector import Vector

from pyflexy.util.Log import Log

class Couple_Table( object ):
    """table of set of (roll, pitch, yaw) coordinates for each couple
    """
    LOG = Log( name='pyflexy.hardware_demon.Couple_Table', level=Log.DEBUG )
    
    SENSORS = [ # (lat, lon)
        (31.7, 0.0),    # 0
        (-31.7, 0.0),   # 1
        (0.0, 66.4),    # 2
        (0.0, -66.4) ]  # 3

    SENSOR_RADIUS = 30.0
        
    class Ball( object ):
        """gives (lat, lon) of any emitter given (roll, pitch, yaw) of ball
        """

        EMITTERS = [ # (lat, lon)
            (0.0, 0.0),         # 0
            (0.0, 63.0),        # 1
            (62.3, 31.7),       # 2
            (49.6, -58.3),      # 3
            (-49.6, -58.3),     # 4
            (-62.3, 31.7),      # 5
            (-130.4, 121.7),    # 6
            (130.4, 121.7),     # 7
            (117.7, -148.3),    # 8
            (0.0, -116.6),      # 9
            (-117.7, -148.3) ]  # 10

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
            latlon[0] += self.angle[1]
            latlon[1] += self.angle[2]
            return latlon

    def __init__( self, granularity=10 ):
        """generate couple table at given granularity
        """
        self._couples = {} # dict of coord set for each (sensor, emitter) pair

        for sensor in range( 4 ):
            
            # get lat, lon vector for sensor
            sensor_latlon = Vector( *self.SENSORS[sensor] )
            
            for emitter in range( 11 ):

                print ".",
                
                ball = self.Ball()

                # create set for couple
                coord_set = set()
                
                # test each coordinate at given granularity
                for roll in range( -180, 180 + granularity, granularity ):
                    for pitch in range( -100, 100 + granularity, granularity ):
                        for yaw in range( -50, 50 + granularity, granularity ):

                            # get lat, lon vector for ball angle
                            ball.angle = [roll, pitch, yaw]
                            vector = ball.emitter_angle( emitter )

                            # get distance to sensor lat, lon coord
                            vector.subtract( sensor_latlon )
                            distance = vector.get_magnitude()
                            
                            # if distance is less than sensor radius add to set
                            if distance < self.SENSOR_RADIUS:
                                coord_set.add( (roll, pitch, yaw) )
                            
                # add set with couple as key
                self._couples[(sensor, emitter)] = coord_set

    def get_coords( self, *couples ):
        """returns set of coords matching list of (sensor, emitter) couples
        """
        couples = list( couples )
        coord_set = self._couples[couples.pop()]
        while couples:
            coord_set &= self._couples[couples.pop()]

        return coord_set

    def get_bounds( self, *couples ):
        """returns bounding coords for list of (sensor, emitter) couples
        """
        bounds = [ [0, 0], [0, 0], [0, 0] ]

        for coords in self.get_coords( *couples ):
            for coord, minmax in zip( coords, bounds ):
                if coord < minmax[0]:
                    minmax[0] = coord
                elif coord > minmax[1]:
                    minmax[1] = coord

        return bounds
        
        
        
        
        
