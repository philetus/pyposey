from threading import Thread, Lock

from Hub_Node import Hub_Node
from Strut_Node import Strut_Node
from pyposey.util.Log import Log

class Assembly_Graph( Thread ):
    """pulls assembly events from queue and builds graph
    """
    LOG = Log( name='pyflexy.assembly_graph.Assembly_Graph', level=Log.DEBUG )

    EVENTS = ( "create", "destroy", "connect", "disconnect", "configure" )

    def __init__( self, event_queue, part_library ):
        Thread.__init__( self )

        self.event_queue = event_queue
        self.part_library = part_library # dictionary of part info by number
        self.roots = [] # list of root hubs
        self.nodes = {} # dict of nodes by number
        self.lock = Lock() # graph modify lock
        self.observers = [] # list of observer functions to call on change

    def run( self ):
        """read events from queue and update scene graph
        """        
        while self.event_queue is not None:

            # block until event is read
            event = self.event_queue.get()

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
        # generate new hub node
        number = event["hub"]
        sockets = self.part_library[number]["sockets"]
        hub = Hub_Node( number=number, sockets=sockets )

        # add it to node set and root node list
        self.nodes[number] = hub
        self.roots.append( hub )

    def _destroy( self, event ):
        """remove hub node

           hub should not still be connected, so it should be in root list
           if hub is not in root list a ValueError is raised
           if hub does not exist a KeyError is raised
        """
        number = event["hub"]
        
        hub = self.nodes[number]
        if hub in self.roots:
            self.roots.remove( hub )
        del self.nodes[number]
        
    def _connect( self, event ):
        """connect hub socket to strut ball
        """
        hub_number = event["hub"]
        socket_number = event["socket"]
        strut_number = event["strut"]
        ball_number = event["ball"]
        
        # get hub
        hub = self.nodes[hub_number]

        # if strut doesn't exist create it
        if not self.nodes.has_key( strut_number ):
            self.nodes[strut_number] = Strut_Node( number=strut_number )

        # get strut
        strut = self.nodes[strut_number]

        # if hub is in root node list, and socket is connected to root
        # already, remove hub from root list
        if hub in self.roots:

            # get set of nodes in graph
            graph_set = self._set_from_graph( strut )

            # get set of other root hubs
            root_set = set( self.roots ) - set( [hub] )

            if len( graph_set & root_set ) > 0:
                self.roots.remove( hub )
        
        # connect socket to ball
        hub.connect_socket( number=socket_number,
                            ball=strut.balls[ball_number] )


    def _set_from_graph( self, seed_node ):
        """traverses graph starting at given node and builds set of all nodes
        """
        visited = set() # nodes in graph that have been visited
        seen = set([ seed_node ]) # nodes in graph seen but not visited

        # pop nodes from seen set while it isn't empty
        while seen:
            node = seen.pop()

            # visit node and add unvisited children to seen set
            for child in node.get_children():
                if child not in visited:
                    seen.add( child )

            # add node to visited set
            visited.add( node )

        return visited

    def _disconnect( self, event ):
        """disconnect hub socket from strut
        """
        hub_number = event["hub"]
        socket_number = event["socket"]
    
        # get hub
        hub = self.nodes[hub_number]

        try:
            
            # get strut
            strut = hub.get_connected_strut( socket_number )

            # disconnect ball and socket
            hub.disconnect_socket( socket_number )
            
            # if strut has no connections delete it
            if strut.connected_hubs() == 0:
                del self.nodes[strut.number]

        except ValueError, error:
            self.LOG.error( error )
            
    def _configure( self, event ):
        """change roll, pitch and yaw of socket
        """
        # get hub
        hub = self.nodes[event["hub"]]

        # change socket angle
        try:
            hub.set_socket_angle( number=event["socket"],
                                  roll=event["roll"],
                                  pitch=event["pitch"],
                                  yaw=event["yaw"] )
        except ValueError, error:
            self.LOG.error( error )
        
