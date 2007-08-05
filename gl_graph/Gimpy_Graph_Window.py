import gtk

from pyposey.assembly_graph.Assembly_Graph import Assembly_Graph

from Gimpy_Camera import Gimpy_Camera
from GL_Graph_Visitor import GL_Graph_Visitor

class Gimpy_Graph_Window( gtk.Window ):
    """window for rendering a posey assembly with opengl

       takes a part library and an assembly event queue as arguments
       
       uses gl graph visitor to walk assembly graph and render it to a
       gimpy camera opengl widget
    """

    def __init__( self, part_library, event_queue, title="gimpy graph window",
                  size=(800, 600) ):
        # gtk window init
        gtk.Window.__init__( self )

        # load assembly graph with event queue and part library and start it
        self.assembly_graph = Assembly_Graph( event_queue=event_queue,
                                              part_library=part_library )
        self.assembly_graph.start()


        # load gl graph renderer to render assembly graph
        self.graph_visitor = GL_Graph_Visitor( self.assembly_graph )

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
        self.assembly_graph.observers.append( self.redraw )

        # variable to hold currently selected graph node
        self.selected = None

    def handle_quit( self ):
        """do some stuff when window is closed
        """
        pass

    def handle_draw( self ):
        """call gl graph visitor to render assembly graph
        """
        self.graph_visitor.draw()

    def handle_press( self, x, y ):
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
            node = self.assembly_graph[address]
            self.selected = node
            node.selected = True

        # redraw window
        self.redraw()
        
    def redraw( self ):
        """add a redraw request to opengl widget event queue
        """
        self.camera.queue_draw()

    def _on_quit( self, widget ):
        self.handle_quit()
        gtk.main_quit()
        
