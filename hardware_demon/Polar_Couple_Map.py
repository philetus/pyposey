import math
from struct import pack, unpack
from numpy import array
from l33tC4D.vector.Polar_Vector3 import Polar_Vector3
from l33tC4D.vector.Matrix3 import Matrix3
from pyposey.util.Log import Log
from Map_Ball import Map_Ball
from Map_Socket import Map_Socket

class Polar_Couple_Map:
    """
    """
    LOG = Log( name='pyposey.hardware_demon.Polar_Couple_Map', level=Log.WARN )
    
    def __init__( self, step=10, filename="couples.map" ):
        self.step = step
        self.nodes = {}
        self.couples = {}

        print "map[",

        # try to load map
        try:
            self._load_map( filename )

        # otherwise build it
        except Exception, error:
            self._build_map()
            self._write_map( filename )
            
        print "]"
        
    def get_coords( self, *couples ):
        """build list of possible coordinate nodes given list of couples
        """
        # if no couples return empty set
        if len( couples ) < 1:
            return set()
        
        self.LOG.info( "couples: %s" % str(couples) )
        
        visible = set( couples )
        not_visible = set( self.couples.keys() ) - visible

        # intersect nodes of visible couples to generate initial possible set
        possible = set( self.couples[couples[0]] )
        for couple in couples[1:]:
            seen = self.couples[couple]
            new = possible & seen

            # if intersection would remove all members of set reject it
            if len( new ) < 1:
                self.LOG.warn( "rejecting seen couple %s!" % str(couple) )
                
            else:
                possible = new

        # subtract nodes of not visible couples to further reduce set
        for couple in not_visible:
            unseen = self.couples[couple]
            new = possible - unseen

            # if subtraction would reduce all members of set reject it
            if len( new ) < 1:
                self.LOG.warn( "rejecting unseen couple %s" % str(couple) )
            else:
                possible = new
                
        return tuple( possible )
    
    def _build_map( self ):
        up = Polar_Vector3().set_heading( 0, 0 )

        # matrix to rotate one step
        rotate_step = Matrix3().rotate( self.step, up )
        
        map_ball = Map_Ball()
        map_socket = Map_Socket( map_ball )
        
        # generate (lat, lon, rot) keys for nodes at given distribution
        for lat in range( 0, 110, self.step ):

            #print ">",
            
            # calculate lon step at lat
            lon_step = 360
            if lat > 0:
                lon_step = int( self.step / math.cos(math.radians(90-lat)) )

            for lon in range( 0, 360, lon_step ):

                # ignore area covered by grips:
                #   lat > 45 and 15 < lon < 165
                #   lat > 45 and 195 < lon < 345
                if lat > 45 and (( 15 < lon and lon < 165)
                                 or (195 < lon and lon < 345)):
                    print "x",

                else:
                    print ">",
                    
                    # matrix to transform to map position
                    transform = None

                    # if lat is 0 we are already at heading
                    if lat == 0:
                        transform = Matrix3()

                    # otherwise generate transform to move to heading
                    else:
                        
                        # generate heading and axis of rotation
                        heading = Polar_Vector3().set_heading( lat, lon )
                        angle = up.angle_to( heading )
                        axis = Polar_Vector3( heading ).cross( up )

                        # build transform to map heading
                        transform = Matrix3().rotate( angle, axis )

                    # transform map ball to heading
                    map_ball.reset()
                    map_ball.transform( transform )

                    # add key for each rotation
                    for rot in range( 0, 360, self.step ):

                        #print ".",
                        #print "<%d %d %d>" % (lat, lon, rot),

                        # get angle from each sensor to each emitter
                        couples = map_socket.get_couples()

                        # add visible couples to this node
                        self.nodes[lat, lon, rot] = couples

                        # add node to each visible couple
                        for couple in couples:
                            if couple not in self.couples:
                                self.couples[couple] = set()
                            self.couples[couple].add( (lat, lon, rot) )

                        # rotate one step around heading
                        transform.transform( rotate_step )
                        map_ball.reset()
                        map_ball.transform( transform )

    def _load_map( self, filename ):
        """load couple map from binary file
        """
        map_file = open( filename, "rb" )
        try:
            self.couples = {}

            # read number of couples in map file
            num_couples = unpack( "h", map_file.read(2) )[0]

            # read couples in from file
            for i in range( num_couples ):

                print "/",

                # read couples and number of coords for couple
                sensor, emitter, num_coords = unpack( "hhh", map_file.read(6) )

                # read coords
                self.couples[sensor, emitter] = set()
                for j in range( num_coords ):
                    lat, lon, rot = unpack( "hhh", map_file.read(6) )
                    self.couples[sensor, emitter].add( (lat, lon, rot) )
                    
        finally:
            map_file.close()

    def _write_map( self, filename ):
        """write couple map to binary map file
        """
        map_file = open( filename, "wb" )
        try:

            # write number of couples'
            couples = sorted( self.couples )
            map_file.write( pack("h", len(couples)) )

            # write each couple
            for sensor, emitter in couples:
                print ".",
                
                coords = sorted( self.couples[sensor, emitter] )

                # write couple and number of coords
                map_file.write( pack("hhh", sensor, emitter, len(coords)) )

                # write each coord
                for coord in coords:
                    map_file.write( pack("hhh", *coord) )
    
        finally:
            map_file.close()
            
