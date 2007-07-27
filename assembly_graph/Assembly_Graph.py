from threading import Thread, Lock

from pyposey.util.Log import Log

from Assembly_Subgraph import Assembly_Subgraph

class Assembly_Graph( Thread ):
    """pulls assembly events from queue and builds graph
    """
    LOG = Log( name='pyflexy.assembly_graph.Assembly_Graph', level=Log.INFO )

    EVENTS = set([ "create", "destroy", "connect", "disconnect", "configure" ])

    def __init__( self, event_queue, part_library ):
        Thread.__init__( self )

        # event queue to pull events from
        self.event_queue = event_queue

        # part library to generate part by address
        self.part_library = part_library
        
        self.subgraphs = [] # list of subgraphs of connected parts
        self.parts = {} # dict of parts by address
        
        self.lock = Lock() # graph modify lock
        self.observers = [] # list of observer functions to call on change

    def run( self ):
        """read events from queue and update node graph
        """        
        while self.event_queue is not None:

            # block until event is read
            event = self.event_queue.get()

            self.LOG.debug( "got event: " + str(event) )

            # acquire graph modify lock and be sure to release it
            self.lock.acquire()
            try:

                # call helper method for event type
                # self.__getattribute__( "f" )( x ) -> self.f( x )
                if not event["type"] in self.EVENTS:
                    raise ValueError( "unrecognized event type: '%s'"
                                      % str(event["type"]) )
                self.__getattribute__( "_" + event["type"] )( event )
                    
            finally:
                self.lock.release()

            # call observer functions
            for observer in self.observers:
                observer()

    def _create( self, event ):
        """create new hub node and add it to node set
        """
        # create new subgraph to hold new hub
        subgraph = Assembly_Subgraph()
        
        # get new hub from part library
        address = event["hub"]
        hub = self.part_library[address]

        # add hub to part set and subgraph
        self.parts[address] = hub
        subgraph.add( hub )

        # add subgraph to subgraphs list
        self.subgraphs.append( subgraph )

    def _destroy( self, event ):
        """remove hub node
        """
        address = event["hub"]

        # get hub by address
        hub = self.parts[address]

        # get hub's subgraph
        subgraph = hub.subgraph

        # remove hub from parts dictionary
        del self.parts[address]

        # remove hub from subgraph
        subgraph.remove( hub )

        # if subgraph is not empty print a warning, otherwise delete it
        if len( subgraph ) > 0:
            self.LOG.error( "destroyed hub not disconnected!" )
        else:
            self.subgraphs.remove( subgraph )
        
    def _connect( self, event ):
        """connect hub socket to strut ball
        """
        hub_address = event["hub"]
        socket_index = event["socket"]
        strut_address = event["strut"]
        ball_index = event["ball"]
        
        # get hub
        hub = self.parts[hub_address]

        # if strut doesn't exist create it and add it to hub's subgraph
        strut = None
        if not self.parts.has_key( strut_address ):
            strut = self.part_library[strut_address]
            self.parts[strut_address] = strut
            hub.subgraph.add( strut )

        # otherwise resolve subgraphs
        else:
            strut = self.parts[strut_address]

            # if subgraphs are different move parts from hub's subgraph
            # to strut's
            if strut.subgraph is not hub.subgraph:
                deadgraph = hub.subgraph
                while len( deadgraph ) > 0:
                    part = deadgraph.pop()
                    strut.subgraph.add( part )
                self.subgraphs.remove( deadgraph )

        # connect ball and socket
        socket = hub[socket_index]
        ball = strut[ball_index]
        socket.connect( ball )

    def _set_from_graph( self, seed_part ):
        """traverses graph starting at given part and builds set of all parts
        """
        visited = set() # nodes in graph that have been visited
        seen = set([ seed_part ]) # nodes in graph seen but not visited

        # pop nodes from seen set while it isn't empty
        while seen:
            part = seen.pop()

            # visit part and add unvisited children to seen set
            for child in part.get_connected():
                if child not in visited:
                    seen.add( child )

            # add part to visited set
            visited.add( part )

        return visited

    def _disconnect( self, event ):
        """disconnect socket of hub from strut
        """
        hub_address = event["hub"]
        socket_index = event["socket"]
    
        # get hub and socket
        hub = self.parts[hub_address]
        socket = hub[socket_index]

        # get ball and strut
        ball = socket.ball
        strut = ball.strut

        # disconnect socket
        socket.disconnect()

        # if strut is no longer connected just remove it
        if len( strut.get_connected() ) < 1:
            strut.subgraph.remove( strut )
            del self.parts[strut.address]
            return

        # if strut subgraph is no longer connected move it to new subgraph
        strut_graph_set = self._set_from_graph( strut )
        if hub not in strut_graph_set:
            subgraph = Assembly_Subgraph()
            for part in strut_graph_set:
                hub.subgraph.remove( part )
                subgraph.add( part )
            self.subgraphs.append( subgraph )
            
    def _configure( self, event ):
        """change roll, pitch and yaw of socket
        """
        # get hub
        hub = self.parts[event["hub"]]

        # change socket angle
        socket_index = event["socket"]
        socket = hub[socket_index]
        socket.set_angle( roll=event["roll"],
                          pitch=event["pitch"],
                          yaw=event["yaw"] )
        
