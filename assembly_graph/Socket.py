from l33tC4D.vector.Matrix3 import Matrix3
from l33tC4D.vector.Polar_Vector3 import Polar_Vector3
from pyposey.util.Log import Log
from Child import Child

class Socket( Child ):
    """a socket of a hub
    """

    LOG = Log( name='pyposey.assembly_graph.Socket', level=Log.WARN )
    EPSILON = 0.1
    FAVORED_RADIUS = 20.0 # favor new coords at this distance over closer coords
    UP = Polar_Vector3().set_heading( 0, 0 )
    X = Polar_Vector3( (1, 0, 0) )

    def __init__( self, parent, index, transform=None ):

        # list of possible (lon, lat, rot) coords
        self.coords = tuple()
        self.current_coords = (0, 0, 0)

        # superclass init builds initial transforms
        Child.__init__( self, parent, index, transform )

    def __repr__( self ):
        return "<socket %d.%d.%d />" % self.address

    def set_coords( self, *coords ):
        """set list of possible (lon, lat, rot) coords
        """
        self.coords = tuple(coords)

        # select next coord
        self._pick_coords()

        # rebuild rotate in transform
        self._build_transforms()
        
    def connect( self, ball ):
        """connect this socket to given ball
        """
        # make sure ball and socket are disconnected
        assert self.connected is None
        assert ball.connected is None

        self.connected = ball
        ball.connected = self

    def disconnect( self ):
        """
        """
        if self.connected is None:
            self.LOG.error( "disconnecting but socket not connected!" )
        self.connected.connected = None
        self.connected = None

    def get_connected_hub( self ):
        """return hub connected to this socket with a strut
        """
        if self.connected is None:
            return None

        # get opposite ball
        ball = self.connected
        strut = ball.parent
        opposite_ball = strut[1-ball.index]
        opposite_socket = opposite_ball.connected
        if opposite_socket is None:
            return None

        # return hub connected to opposite ball
        return opposite_socket.parent

    def _pick_coords( self ):
        """pick new current coords from set of possible coords
        """
        # if there is only one possible coord just set it
        if len(self.coords) < 2:
            self.current_coords = self.coords[0]
            self.LOG.info( "%s set new forced coords %s"
                           % (str(self), str(self.current_coords)) )
            return

        # otherwise build dictionary of coords by distance from current coord
        # and pick closest coords
        heading = Polar_Vector3().set_heading( *self.current_coords[:2] )
        rotation = self.current_coords[2]
        distances = {}
        new_heading = Polar_Vector3()

        self.LOG.debug( "calculating distances from coords %s:"
                        % str(self.current_coords) )
        
        for coords in self.coords:

            # get distance to new heading
            new_heading.set_heading( *coords[:2] )
            distance = heading.angle_to( new_heading )
            
            # add distance between rotations
            rot_distance = abs( rotation - coords[2] )
            if rot_distance > 180.0:
                rot_distance = 360.0 - rot_distance
            distance += rot_distance

            # add coords to dict by distance, favor some movement
            distances[abs(distance - self.FAVORED_RADIUS)] = (distance, coords)

            self.LOG.debug( "\t%.1f to coords %s" % (distance, str(coords)) )

        # set coord with min favored distance as new coord
        min_favored_distance = min(distances)
        min_distance, self.current_coords = distances[min_favored_distance]
        
        self.LOG.info( "%s picked new coords %s at distance %.1f"
                       % (str(self), str(self.current_coords), min_distance) )
        
    def _build_transforms( self ):
        if self._transform is None:
            self.in_transform = None
            self.out_transform = None
            return

        # build transform for rotation from socket to ball
        rotation = Matrix3()

        # generate heading, axis and angle
        heading = Polar_Vector3().set_heading( *self.current_coords[:2] )
        angle = self.UP.angle_to( heading )

        # if angle to heading is nonzero rotate angle around axis
        if angle > self.EPSILON and angle + self.EPSILON < 180.0:
            axis = Polar_Vector3( heading ).cross( self.UP )
            rotation.rotate( angle, axis )
            
        rotation.rotate( self.current_coords[2], self.UP )
        
        # build out transform
        self.out_transform = Matrix3( self._transform )

        # apply inverse ball rotation to base transform to rotate back to ball
        self.out_transform.transform( rotation )

        # build in transform
        self.in_transform = Matrix3()

        # rotate 180 degrees around x axis to face in
        self.in_transform.rotate( 180, self.X )

        # apply inverse rotation
        self.in_transform.transform( rotation.invert() )

        # apply inverted base matrix to move to parent origin
        self.in_transform.transform( Matrix3(self._transform).invert() )

        

