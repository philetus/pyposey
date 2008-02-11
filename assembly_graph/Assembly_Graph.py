from threading import Thread, Lock
from pyposey.util.Log import Log
from Assembly_Subgraph import Assembly_Subgraph
from Graph_Visitor import Graph_Visitor

class Assembly_Graph( Thread ):
    """pulls assembly events from queue and builds graph
    """
    LOG = Log( name='pyflexy.assembly_graph.Assembly_Graph', level=Log.INFO )

    EVENTS = set([ "create", "destroy", "connect", "disconnect", "configure" ])

    def __init__( self, event_queue, part_library, orient=False ):
        Thread.__init__( self )

        # event queue to pull events from
        self.event_queue = event_queue

        # part library to generate part by address
        self.part_library = part_library
        
        self.subgraphs = [] # list of subgraphs of connected parts
        self.parts = {} # dict of parts by address
        
        self.lock = Lock() # graph modify lock
        self.observers = [] # list of observer functions to call on change

        # if orient flag is set, build graph visitor to orient parts on
        # change and add its orient method to the list of graph observers
        if orient:
            self.visitor = Graph_Visitor( self )
            self.observers.append( self.visitor.orient )

            # check part library for transforms
            for part in self.part_library:
                for connector in part:
                    if connector._transform is None:
                        raise ValueError(
                            "oriented assembly graph requires transform for %s!"
                            % str(connector) )

    def __getitem__( self, key ):
        return self.parts[key]

    def __iter__( self ):
        return self.parts.itervalues()

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
                observer(event)

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

        # if hub not in parts dictionary just return
        if address not in self.parts:
            self.LOG.warn( "can't destroy hub %s: doesn't exist!"
                           % str(address) )
            return

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

        # if strut address not in part library just return
        if strut_address not in self.part_library:
            self.LOG.warn( "can't connect to strut %s: not in library!"
                           % str(strut_address) )
            return
        
        # get hub and socket
        hub = self.parts[hub_address]
        socket = hub[socket_index]

        # if ball or socket is already connected disconnect it first
        if socket.connected is not None:
            self.LOG.warn( "%s forced to disconnect from %s!"
                           % (str(socket), str(socket.connected)) )
            self._disconnect({ "hub":hub.address, "socket":socket.index })
        if strut_address in self.parts:
            ball = self.parts[strut_address][ball_index]
            if ball.connected is not None:
                self.LOG.warn( "%s forced to disconnect from %s!"
                               % (str(ball), str(ball.connected)) )
                s = ball.connected
                h = s.parent
                self._disconnect({ "hub":h.address, "socket":s.index })

                # if after forced disconnect hub is no longer connected
                # to anything destroy it
                if len( h.get_connected() ) < 1:
                    self._destroy({ "hub":h.address })
            
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

        # if hub not in parts dictionary just return
        if hub_address not in self.parts:
            self.LOG.warn( "can't disconnect hub %s: doesn't exist!"
                           % str(hub_address) )
            return

        # get hub and socket
        hub = self.parts[hub_address]
        socket = hub[socket_index]

        # if socket is not connected just log warning and return
        if socket.connected is None:
            self.LOG.warn( "can't disconnect %s: not connected!" % str(socket) )
            return

        # get ball and strut
        ball = socket.connected
        strut = ball.parent

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
        # get hub, if there is no hub create it
        hub_address = event["hub"]
        if hub_address not in self.parts:
            self._create({ "hub":hub_address })
        hub = self.parts[hub_address]

        # change socket angle
        socket_index = event["socket"]
        socket = hub[socket_index]
        socket.set_coords( *event["coords"] )

        # if socket not connected, connect it
        if socket.connected is None:
            self._connect( event )
        
