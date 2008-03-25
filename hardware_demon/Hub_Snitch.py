from time import time
from l33tC4D.vector.Vector3 import Vector3
from pyposey.util.Log import Log

class Hub_Snitch( object ):
    """interprets events from one hub and tracks hub state
    """
    LOG = Log( name='pyflexy.hardware_demon.Hub_Snitch', level=Log.INFO )
    ACCEL_ZERO = 508
    ACCEL_G = -100.0
    UP_EPSILON = 15.0
    UPS = 5

    def __init__( self, index=None, queue=None,
                  couple_map=None, snitches=None, probates=None ):
        
        self.index = index # 2 byte hub index
        self.sockets = {} # dict of sockets to track socket state
        self.queue = queue # assembly event queue to write events to
        self.couple_map = couple_map # couple map
        self.snitches = snitches # list of snitches to remove self from
        self.probates = probates

        self.up_values = [ (0.0, 0.0, 1.0) for i in range(self.UPS) ]
        self.last_up = Vector3( (0.0, 0.0, 1.0) )
        

    def interpret( self, event ):
        """takes couple event, updates hub state and generates assembly event        
        """
        # if this is an accelerometer event just generate an up event
        if event["type"] == "accelerometer":
            self._handle_up( event )
            return
            
        # if socket doesn't already exist make new socket or fail
        if not self.sockets.has_key( event["socket_index"] ):
            if not self._make_socket( event ):
                return

        # get event socket
        socket_index = event["socket_index"]
        socket = self.sockets[socket_index]

        # if this is not a zero couple event set couple
        if not self._is_zero_couple( event ):
            try:
                socket.set_couple( strut=event["strut_address"],
                                   ball=event["ball_index"],
                                   sensor=event["sensor_index"],
                                   emitter=event["emitter_index"] )

            except ValueError, error:
                self.LOG.error( error )

            # if socket was on probation clear it
            address = (self.index, socket_index)
            if self.probates.has_key( address ):
                del self.probates[address]
                
        # otherwise clear sensor couple or fail
        else:
            if not socket.clear_couple( event["sensor_index"] ):
                return

        # if there are now no couples put socket on probation
        if len( socket.couples ) < 1:
            address = (self.index, socket_index)
            self.probates[address] = time()

        # otherwise recalculate socket angles and send configure event
        else:
            self._calculate_angle( event )

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

    def _is_zero_couple( self, event ):
        """return true if strut index is all zeros signifying disconnect
        """
        for i in event["strut_address"]:
            if i != 0:
                return False

        return True

    def _make_socket( self, event ):
        """check that this is not a zero couple event, then send events and
           create new socket
        """
        # if this is a zero couple event log warning and fail
        if self._is_zero_couple( event ):
            self.LOG.warn( "zero couple event for disconnected socket: %s"
                           % str(event) )
            return False
            
        # if this is first socket in hub send create event
        if len( self.sockets ) < 1:
            self.queue.put( {"type":"create",
                             "hub":event["hub_address"]} )
                                      
        # send connect event
        self.queue.put( {"type":"connect",
                         "hub":event["hub_address"],
                         "socket":event["socket_index"],
                         "strut":event["strut_address"],
                         "ball":event["ball_index"]} )
 
        # create new socket
        self.sockets[event["socket_index"]] = self.Socket()

        return True

    def remove_socket( self, socket_index ):
        """remove socket and send disconnect event
        """
        # remove socket from probates list
        address = (self.index, socket_index)
        if self.probates.has_key( address ):
            del self.probates[address]

        # remove socket from hub snitch
        del self.sockets[socket_index]

        # send disconnect event
        self.queue.put( {"type":"disconnect",
                         "hub":self.index,
                         "socket":socket_index} )

        # if there are now no sockets send destroy event and remove this
        # hub from snitches list
        if len( self.sockets ) < 1:
            self.queue.put( {"type":"destroy",
                             "hub":self.index} )
            del self.snitches[self.index]

    def _calculate_angle( self, event ):
        """generate new angle values for socket using lookup table for couples
        """
        socket_index = event["socket_index"]
        socket = self.sockets[socket_index]

        # get couples sorted most recent first by timestamp
        stamped_couples = list( socket.couples.values() )
        stamped_couples.sort( reverse=True )

        # make tuple of tuples of couples stripped of timestamps
        couples = tuple( tuple(couple[1:]) for couple in stamped_couples )

        try:
            coords = self.couple_map.get_coords( *couples )

            self.LOG.info( "couples: %s" % str(couples) )
            self.LOG.info( "coords: %s" % str(coords) )
                    
            self.queue.put( {"type":"configure",
                             "hub":self.index,
                             "socket":socket_index,
                             "strut":event["strut_address"],
                             "ball":event["ball_index"],
                             "coords":coords} )
            
        except KeyError:
            self.LOG.warn( "no mapping for couple %s" % str(couple_set) )
            
    class Socket( object ):
        """tracks socket state
        """
        LOG = Log( name='pyposey.hardware_demon.Hub_Snitch.Socket',
                   level=Log.DEBUG )
        SENSORS = 4 # number of sensors per socket
        
        def __init__( self ):
            self.strut = None # index of connected strut
            self.ball = None # index of connected ball
            self.couples = {} # dict of sensor:(stamp,sensor,emitter) couples

        def clear_couple( self, sensor ):
            # if given sensor is not already coupled log warning and fail
            if not self.couples.has_key( sensor ):
                self.LOG.warn( "spurious zero couple event for sensor %d"
                                    % sensor )
                return False

            # otherwise clear couple
            del self.couples[sensor]

            # if there are no more couples disconnect
            if len( self.couples ) < 1:
                self.strut = None
                self.ball = None
                
            return True

        def set_couple( self, strut, ball, sensor, emitter ):
            # if strut and ball are not set set them
            if self.strut is None and self.ball is None:
                self.strut = strut
                self.ball = ball

            # if strut and ball are already set new values should match
            else:
                if self.strut != strut or self.ball != ball:
            
                    raise ValueError(
                        "socket coupled to two balls: %d.%d.%d > %d.%d.%d"
                        % (self.strut[0], self.strut[1], self.ball,
                           strut[0], strut[1], ball) )
            
            self.couples[sensor] = ( time(), sensor, emitter )
