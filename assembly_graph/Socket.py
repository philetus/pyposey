from l33tC4D.vector.Polar_Vector3 import Polar_Vector3
from pyposey.util.Log import Log
from Child import Child

class Socket( Child ):
    """a socket of a hub
    """

    LOG = Log( name='pyposey.assembly_graph.Socket', level=Log.WARN )
    UP = Polar_Vector3().set_heading( 0, 0 )
    X = Polar_Vector3( (1, 0, 0) )

    def __init__( self, parent, index, transform=None ):
        Child.__init__( self, parent, index, transform )

        # list of possible (lon, lat, rot) coords
        self.coords = tuple()
        self.current_coords = (0, 0, 0)

        # generate initial transforms        
        self._build_transforms()

    def __repr__( self ):
        return "<socket %d.%d.%d />" % ( self.parent.address + (self.index,) )

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

    def get_in_transform( self ):
        """return matrix to transform from child to parent
        """
        return self._rotate_in_transform

    def get_out_transform( self ):
        """return matrix to transform from parent to child
        """
        return self._rotate_out_transform

    def _pick_coords( self ):
        """pick new current coords from set of possible coords
        """
        # if there is only one possible coord just set it
        if len(self.coords) < 2:
            self.current_coords = self.coords[0]

        # otherwise build dictionary of coords by distance from current coord
        # and pick closest coords
        heading = Polar_Vector3().set_heading( *self.current_coords[:2] )
        rotation = self.current_coords[2]
        distances = {}
        new_heading = Polar_Vector3()
        for coords in self.coords:

            # get distance to new heading
            new_heading.set_heading( *coords[:2] )
            distance = heading.angle_to( new_heading )

            # add distance between rotations
            rot_distance = abs( rotation - coords[2] )
            if rot_distance > 180.0:
                rot_distance = 360.0 - rot_distance
            distance += rot_distance

            # add coords to dict by distance
            distances[distance] = coords

        # set coord with min distance as new coord
        self.current_coord = distances[min(distances)]
        
    def _build_transforms( self ):
        if self._transform is None:
            self.in_transform = None
            self.out_transform = None
            return

        # generate heading, axis and angle
        heading = Polar_Vector3().set_heading( *self.current_coords[:2] )
        axis = Polar_Vector3( heading ).cross( self.UP )
        angle = self.UP.angle_to( heading )

        # build transform for rotation from ball to socket
        rotation = Matrix3()
        rotation.rotate( angle, axis )
        rotation.rotate( self.current_coords[2], self.UP )

        # build in transform
        i = Matrix3( rotation )

        # rotate 180 degrees around x axis to face out
        i.rotate( 180, self.X )

        # apply inverted base matrix to move to parent origin
        i.transform( Matrix3(self._transform).invert() )
        
        self.in_transform = i

        # build out transform
        o = Matrix3( self._transform )

        # apply inverse ball rotation to base transform to rotate back to ball
        o.transform( rotation.invert() )
