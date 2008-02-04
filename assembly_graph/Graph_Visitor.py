from l33tC4D.vector.Matrix3 import Matrix3
from l33tC4D.vector.Vector3 import Vector3

from pyposey.util.Log import Log

class Graph_Visitor:
    """updates 3d orientation matrices of hubs and struts
    """
    LOG = Log( name='pyposey.assembly_graph.Graph_Visitor',
               level=Log.INFO )
    UP = Vector3( (0, 0, 1) )
    
    def __init__( self, assembly_graph ):
        """
        """
        # assembly graph to render
        self.graph = assembly_graph

        # nodes visited during rendering
        self.visited = None

    def orient( self ):
        """traverse graph and set position and orientation of hubs and struts
        """
        # acquire assembly graph lock before traversing graph
        self.graph.lock.acquire()
        try:

            # start at root of each subgraph
            for hub in (subgraph.root for subgraph in self.graph.subgraphs):

                # init visited set
                self.visited = set()

                # seed orientation with up vector
                self._seed_with_up_vector( hub )
                
                # visit hub and orient it
                try:
                    self._visit_node( hub )
                except Exception, error:
                    self.LOG.error( "visit hub failed: " + str(error) )

                # clear visited set
                self.visited = None
                
        finally:
            self.graph.lock.release()

    def _seed_with_up_vector( self, hub ):
        """set hub orientation to transform z axis to up vector
        """
        # clear hub orientation
        hub.align()
        
        # if there is no up vector just return
        if hub.up is None:
            return

        # otherwise axis is cross product with z axis
        axis = Vector3( self.UP ).cross( hub.up )

        # angle is angle to z axis
        angle = self.UP.angle_to( hub.up )

        # set hub orientation using angle and axis
        hub.rotate( angle, axis )
        

    def _visit_node( self, node ):
        """orient children relative to this node
        """
        self.LOG.debug(  "visiting node ", node.address )
        
        # add to visited set
        self.visited.add( node )

        # visit children and orient relative to hub
        for child in node:
            other_child = child.connected
            if other_child is not None:
                other_node = other_child.parent
                if other_node not in self.visited:

                    # seed orientation with node orientation
                    other_node.align( node )
                
                    # transform out to child
                    other_node.transform( child.out_transform )
                    
                    # transform in from other child
                    other_node.transform( other_child.in_transform )

                    # visit other node
                    self._visit_node( other_node )
