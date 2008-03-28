from time import time
from l33tC4D.vector.Vector3 import Vector3
from pyposey.util.Log import Log

class Hub_Snitch( object ):
    """interprets events from one hub and tracks hub state
    """
    LOG = Log( name='pyflexy.hardware_demon.Hub_Snitch', level=Log.WARN )
    ACCEL_ZERO = 508
    ACCEL_G = -100.0
    UP_EPSILON = 5.0
    UPS = 5

    def __init__( self, index=None, queue=None, couple_map=None ):
        
        self.index = index # 2 byte hub index
        self.sockets = {} # dict of sockets to track socket state
        self.queue = queue # assembly event queue to write events to
        self.couple_map = couple_map # couple map

        self.up_values = [ (0.0, 0.0, 1.0) for i in range(self.UPS) ]
        self.last_up = Vector3( (0.0, 0.0, 1.0) )
        

    def interpret( self, event ):
        """takes couple event, updates hub state and generates assembly event        
        """
        # if this is an accelerometer event just generate an up event
        if event["type"] == "accelerometer":
            self._handle_up( event )
            return

        # get event data
        hub_address = event["hub_address"]
        socket_index = event["socket_index"]
        strut_address = event["strut_address"]
        ball_index = event["ball_index"]

        # if there is no strut connected just remove socket
        if strut_address is None:
            self._remove_socket( socket_index )
            return

        # if socket doesn't already exist make new socket
        if socket_index not in self.sockets:
            self._make_socket( socket_index, strut_address, ball_index )

        # get event socket
        socket = self.sockets[socket_index]

        # if socket is connected to different ball disconnect and
        # connect to new ball
        if( socket.ball_index != ball_index
            or socket.strut_address != strut_address ):

            self.LOG.warn( "forced disconnect from socket!" )
            
            socket.set_ball( strut_address, ball_index )
            self._put_disconnect( socket_index )
            self._put_connect( socket_index )

        # set emitter values for socket and calculate angles on change
        self._set_couples( socket_index, event["coupled_emitters"] )

    def _handle_up( self, event ):
        """update running average of up values, trigger event on change
        """
        # normalize raw values to 1.0 ~= g
        x = (event["x"] - self.ACCEL_ZERO) / self.ACCEL_G
        y = (event["y"] - self.ACCEL_ZERO) / -self.ACCEL_G # y is backwards?
        z = (event["z"] - self.ACCEL_ZERO) / self.ACCEL_G

        # add new up values on end
        self.up_values.append( (x, y, z) )
        self.up_values.pop( 0 )
        
        # calculate new average
        new_up = Vector3([ sum(z) / self.UPS for z in zip(*self.up_values) ])

        # if change is smaller than epsilon just return
        if self.last_up.angle_to( new_up ) < self.UP_EPSILON:
            return

        self.last_up = new_up
        self.queue.put( {"type":"up",
             "hub":event["hub_address"],
             "x":new_up[0],
             "y":new_up[1],
             "z":new_up[2]
            } )

    def _make_socket( self, socket_index, strut_address, ball_index ):
        """create new socket and send events
        """            
        # if this is first socket in hub send create event
        if len( self.sockets ) < 1:
            self.queue.put( {"type":"create",
                             "hub":self.index} )
                                      
        # create new socket
        self.sockets[socket_index] = self.Socket( strut_address, ball_index )

        # send connect event
        self._put_connect( socket_index )

    def _put_connect( self, socket_index ):
        socket = self.sockets[socket_index]
        self.queue.put( {"type":"connect",
                         "hub":self.index,
                         "socket":socket_index,
                         "strut":socket.strut_address,
                         "ball":socket.ball_index} )
 
    def _remove_socket( self, socket_index ):
        """remove socket and send disconnect event
        """
        # if socket has already been removed just return
        if socket_index not in self.sockets:
            return
        
        # remove socket from hub snitch
        del self.sockets[socket_index]

        # send disconnect event
        self._put_disconnect( socket_index )

        # if there are now no sockets send destroy event
        if len( self.sockets ) < 1:
            self.queue.put( {"type":"destroy",
                             "hub":self.index} )
            
    def _put_disconnect( self, socket_index ):
        self.queue.put( {"type":"disconnect",
                         "hub":self.index,
                         "socket":socket_index} )

    def _set_couples( self, socket_index, emitters ):
        """set couples and recalculate angle on change
        """
        socket = self.sockets[socket_index]
        
        # if there is no change just return
        emitters = list(emitters)
        if socket.couples == emitters:
            return

        # set new emitters list
        socket.couples = emitters

        # make list of couples to recalculate angle
        couples = [ (i, emitters[i]) for i in range(len(emitters))
                    if emitters[i] is not None ]

        # get list of coords from couple map
        coords = self.couple_map.get_coords( *couples )
        
        self.LOG.info( "\n\ncouples: %s" % str(couples) )
        self.LOG.info( "coords: %s" % str(coords) )

        # put configure event on queue
        self.queue.put( {"type":"configure",
                         "hub":self.index,
                         "socket":socket_index,
                         "strut":socket.strut_address,
                         "ball":socket.ball_index,
                         "coords":coords} )
            
    class Socket( object ):
        """tracks socket state
        """
        SENSORS = 4 # number of sensors per socket
        
        def __init__( self, strut_address, ball_index ):
            self.strut_address = None # index of connected strut
            self.ball_index = None # index of connected ball
            self.couples = None # list of emitters for each sensor

            self.set_ball( strut_address, ball_index )

        def set_ball( self, strut_address, ball_index ):
            self.strut_address = strut_address
            self.ball_index = ball_index
            self.couples = [None] * self.SENSORS

                
