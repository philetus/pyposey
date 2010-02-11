import gtk
from pyposey.util.Log import Log
from Gimpy_Camera import Gimpy_Camera

class Gimpy_Graph_Window( gtk.Window ):
    """window for rendering a posey assembly with opengl

       takes a part library and an assembly event queue as arguments
       
       uses gl graph visitor to walk assembly graph and render it to a
       gimpy camera opengl widget
    """
    LOG = Log( name='pyposey.gl_graph.Gimpy_Graph_Window', level=Log.INFO )

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

        # add gtk opengl draw area widget to window      
        self.camera = Gimpy_Camera()        
        self.add( self.camera )

        # connect events
        self.set_events( gtk.gdk.KEY_RELEASE_MASK |
                         gtk.gdk.KEY_PRESS_MASK )
        self.connect( "key_press_event", self._on_key_press )
        self.connect( "key_release_event", self._on_key_release )
        self.connect( "destroy", self._on_quit )
        
        # tracks currently pressed keys
        self.keyset = set()

        # anchor coords for mouse zoom
        self.zoom_anchor = (1.0, 0) # zoom, y coord

        # connect camera handlers to local methods
        self.camera.handle_draw = self.handle_draw
        self.camera.handle_press = self.handle_press
        self.camera.handle_motion = self.handle_motion

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

    def handle_motion( self, x, y ):
        """do something when mouse pointer is moved

           hold space to rotate around z, ctrl to zoom
        """
        # only do stuff when we are dragging
        if self.camera.pointer_down:
            redraw = False
            
            if 65505 in self.keyset: # 65505 -> <lshift>
                self.camera.rotation = x
                redraw = True

            if 65507 in self.keyset: # 65507 -> <ctrl>
                zoom = self.zoom_anchor[0] + ((self.zoom_anchor[1] - y) / 100.0)
                self.camera.zoom = max( zoom, 0.1 )
                self.LOG.debug( "new zoom: %.1f %d"
                                % (self.camera.zoom, y) )
                redraw = True

            if redraw:
                self.redraw()

    def handle_press( self, x, y ):
        # if no keys are pressed select graph node under pointer
        if len(self.keyset) < 1:
            self.LOG.debug( "no keys held; selecting" )
            self._select_node( x, y )
            self.redraw()

        # if <ctrl> is pressed set anchor position for zoom
        elif 65507 in self.keyset:
            self.zoom_anchor = (self.camera.zoom, y)
            self.LOG.debug( "zoom anchored at: %.1f %d" % self.zoom_anchor )
        
    def redraw( self ):
        """add a redraw request to opengl widget event queue
        """
        self.camera.queue_draw()

    def _on_quit( self, widget ):
        self.handle_quit()
        gtk.main_quit()

    def _on_graph_event( self, event ):
        self.redraw()

    def _on_key_press( self, widget, event ):
        self.keyset.add( event.keyval )
        self.LOG.debug( "key pressed: '%s' <%d>"
                        % (event.string, event.keyval) )
        return True

    def _on_key_release( self, widget, event ):
        self.keyset.discard( event.keyval )
        self.LOG.debug( "key released: '%s' <%d>"
                        % (event.string, event.keyval) )
        return True


