import gtk
from Gimpy_Camera import Gimpy_Camera

class Gimpy_Graph_Window( gtk.Window ):
    """window for rendering a posey assembly with opengl

       takes a part library and an assembly event queue as arguments
       
       uses gl graph visitor to walk assembly graph and render it to a
       gimpy camera opengl widget
    """

    def __init__( self, assembly_graph, title="gimpy graph window",
                  size=(800, 600) ):
        self.graph = assembly_graph

        # gtk window init
        gtk.Window.__init__( self )

        # set title and size
        self.set_title( title )
        self.resize( *size )

        # ???
        self.set_reallocate_redraws( True )

        # connect destroy event
        self.connect( "destroy", self._on_quit )

        # add gtk opengl draw area widget to window      
        self.camera = Gimpy_Camera()        
        self.add( self.camera )
        
        # connect camera handlers to local methods
        self.camera.handle_draw = self.handle_draw
        self.camera.handle_press = self.handle_press

        # add redraw call to assembly graph observer methods
        self.graph.observers.append( self._on_graph_event )

        # variable to hold currently selected graph node
        self.selected = None

    def handle_quit( self ):
        """do some stuff when window is closed
        """
        pass

    def handle_draw( self ):
        """call each node to draw itself
        """
        # acquire assembly graph lock before drawing nodes
        self.graph.lock.acquire()
        try:

            for node in self.graph:
                node.draw()

        finally:
            self.graph.lock.release()

    def _select_node( self, x, y ):
        """set selected graph node when pointer is pressed
        """
        # clear currently selected node
        if self.selected is not None:
            self.selected.selected = False
            self.selected = None
        
        # get list of gl names sorted by depth
        gl_names = self.camera.select( x, y )

        # if there were nodes under pointer get address from top gl name
        # and select node
        if gl_names:
            gl_name = gl_names[0]
            address = (gl_name / 256), (gl_name % 256)
            node = self.graph[address]
            self.selected = node
            node.selected = True

    def handle_press( self, x, y ):
        # select top node under pointer
        self._select_node( x, y )

        # redraw window
        self.redraw()
        
    def redraw( self ):
        """add a redraw request to opengl widget event queue
        """
        self.camera.queue_draw()

    def _on_quit( self, widget ):
        self.handle_quit()
        gtk.main_quit()

    def _on_graph_event( self, event ):
        self.redraw()
        
