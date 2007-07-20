from xml.sax.saxutils import XMLGenerator
from xml.sax import parse
from xml.sax.handler import ContentHandler

from l33tC4D.vector.Vector3 import Vector3
from pyposey.util.Log import Log

from Ball import Ball
from Socket import Socket

class Couple_Map( object ):
    """maps each (roll, pitch, yaw) coordinate to set of couples
    """
    LOG = Log( name='pyposey.hardware_demon.Couple_Map', level=Log.WARN )
    NEAR_RADIUS = 20.0 # distance to hop

    class Map_Parser( ContentHandler ):
        """parses map data from xml file into couple map
        """

        def __init__( self, couples ):
            self.couples = couples

            self.current_couple_set = None
            self.current_coord_set = None

            self.counter = 0

        def startElement( self, name, attrs ):
            if name == "couple_map":
                pass
            elif name == "couple_set":
                self.current_couple_set = set()
                self.current_coord_set = set()
            elif name == "couple":
                sensor = int( str(attrs["sensor"]) )
                emitter = int( str(attrs["emitter"]) )
                self.current_couple_set.add( (sensor, emitter) )
            elif name == "coord":
                roll = float( str(attrs["roll"]) )
                pitch = float( str(attrs["pitch"]) )
                yaw = float( str(attrs["yaw"]) )
                self.current_coord_set.add( (roll, pitch, yaw) )
            else:
                raise ValueError( "unrecognized tag: '&s'!" % name )

        def endElement( self, name ):
            if name == "couple_set":
                couple_set = frozenset( self.current_couple_set )
                self.couples[couple_set] = self.current_coord_set

                self.current_couple_set = None
                self.current_coord_set = None

                self.counter += 1
                if self.counter > 30:
                    print ">",
                    self.counter = 0

    def __init__( self, granularity=10, filename="couple_map.xml" ):
        """generate couple map at given granularity
        """
        self.couples = {} # set of coords for each couple set

        print "map[",

        # try to load map
        try:
            self._load_map( filename )

        # otherwise build it
        except Exception, error:
            self.LOG.error( error )
            
            # build map
            self._build_map( granularity )

            # write map to file
            self._write_map( filename )

        print "]"

    def _build_map( self, granularity ):
        """builds a copule map
        """
        ball = Ball()
        socket = Socket( ball )
        
        # test each coordinate at given granularity
        for roll in range( -180 + (granularity / 2), 180, granularity ):
            ball.angle[0] = roll
            print ".",
            for pitch in range( -100 + (granularity / 2), 100, granularity ):
                ball.angle[1] = pitch
                for yaw in range( -50 + (granularity / 2), 50, granularity ):
                    ball.angle[2] = yaw

                    # get set of couples for this roll, pitch and yaw
                    couple_set = frozenset( socket.get_couples() )
                    
                    # add coords to couples under set
                    if not self.couples.has_key( couple_set ):
                        self.couples[couple_set] = set()
                    self.couples[couple_set].add( (roll, pitch, yaw) )

    def _write_map( self, filename ):
        """writes couple map to xml file
        """
        # open file to write xml to
        xml_file = open( filename, 'w' )

        # create xmlgenerator to write xml
        writer = XMLGenerator( xml_file )

        # start document
        writer.startDocument()
        writer.characters( "\n" )
        writer.startElement( "couple_map", {} )

        # create entry for each couple set
        for couple_set, coord_set in self.couples.iteritems():
            writer.characters( "\n\t" )
            writer.startElement( "couple_set", {} )

            # write couple for each pair in set
            for sensor, emitter in couple_set:
                attrs = { "sensor":str(sensor), "emitter":str(emitter) }
                writer.characters( "\n\t\t" )
                writer.startElement( "couple", attrs )
                writer.endElement( "couple" )

            # write coord for each coord in set
            for roll, pitch, yaw in coord_set:
                attrs = { "roll":str(roll), "pitch":str(pitch), "yaw":str(yaw) }
                writer.characters( "\n\t\t" )
                writer.startElement( "coord", attrs )
                writer.endElement( "coord" )

            writer.characters( "\n\t" )
            writer.endElement( "couple_set" )

        # end document and close file
        writer.characters( "\n" )
        writer.endElement( "couple_map" )
        writer.endDocument()
        xml_file.close()
        
    def _load_map( self, filename ):
        """loads map from couple file
        """
        xml_file = open( filename )
        handler = self.Map_Parser( couples=self.couples )
        parse( xml_file, handler )
        xml_file.close()

    def get_bounds( self, *couples ):
        """returns (min, max) for roll, pitch and yaw
        """
        bounds = [ [0, 0], [0, 0], [0, 0] ]

        for coords in self.couples[frozenset(couples)]:
            for coord, minmax in zip( coords, bounds ):
                if coord < minmax[0]:
                    minmax[0] = coord
                elif coord > minmax[1]:
                    minmax[1] = coord

        return bounds

    def get_nearest( self, last, *couples ):
        """takes last (roll, pitch, yaw) coords and returns nearest new coords
        """
        nearest_coords = None
        nearest = 1000.0

        # loop through possible coords and select nearest to near radius
        for coords in self.couples[frozenset(couples)]:
            distance = self._get_distance( last, coords )
            
            # if angle is closer to NEAR_RADIUS than current nearest replace
            # current nearest
            if( abs(distance - self.NEAR_RADIUS)
                < abs(nearest - self.NEAR_RADIUS) ):
                nearest_coords = list(coords)
                nearest = distance

        self.LOG.info( "distance from last coords: %f" % nearest )
        return nearest_coords

    def _get_distance( self, a, b ):
        roll_d = min( abs(a[0] - b[0]),
                      abs((360 + a[0]) - b[0]),
                      abs(a[0] - (360 + b[0])) )
        pitch_d = abs( a[1] - b[1] )
        yaw_d = abs( a[2] - b[2] )

        return Vector3( roll_d, pitch_d, yaw_d ).magnitude
        


