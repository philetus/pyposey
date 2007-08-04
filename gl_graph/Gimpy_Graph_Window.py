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
        self.graph_renderer = GL_Graph_Renderer( self.assembly_graph )

        # set title and size
        self.set_title( title )
        self.set_size( *size )

        # ???
        self.set_reallocate_redraws( True )

        # connect destroy event
        self.connect( "destroy", self._on_quit )

        # add gtk opengl draw area widget to window
        self.camera = Gimpy_Camera()        
        self.add( self.camera )

        # connect camera draw handler to local method
        self.camera.handle_draw = self.handle_draw

        # add redraw call to assembly graph observer methods
        self.assembly_graph.observers.append( self.redraw )

    def handle_quit( self ):
        """do some stuff when window is closed
        """
        pass

    def handle_draw( self ):
        """call gl graph renderer to render assembly graph
        """
        self.graph_renderer.draw()

    def redraw( self ):
        """add a redraw request to opengl widget event queue
        """
        self.camera.queue_draw()

    def _on_quit( self ):
        self.handle_quit()
        gtk.main_quit()
        
