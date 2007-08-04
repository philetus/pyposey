import gtk
import gtk.gtkgl
from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import glutSolidTeapot

class Gimpy_Camera( gtk.DrawingArea, gtk.gtkgl.Widget ):
    """gimp toolkit opengl drawing area widget with hooks for event callbacks

       queue_draw() adds redraw request to event queue
    """

    def __init__( self ):          
        # call superclass constructor
        gtk.DrawingArea.__init__( self )

        # set up gl widget
        self._init_gl_widget()

        # connect events to callbacks
        self.set_events( gtk.gdk.POINTER_MOTION_MASK |
                         gtk.gdk.BUTTON_RELEASE_MASK |
                         gtk.gdk.BUTTON_PRESS_MASK )
        self.connect_after( "realize", self._on_realize )
        self.connect( "expose_event", self._on_expose )
        self.connect( "configure_event", self._on_configure )
        self.connect( "motion_notify_event", self._on_motion )
        self.connect( "button_press_event", self._on_press )
        self.connect( "button_release_event", self._on_release )

        # for rotating view
        self.rotation = [ 0, 0, 0 ]

        # flag to track pointer up or down
        self.pointer_down = False

        # eye position and focus
        self.eye = ( 0.0, 0.0, -800.0 )
        self.focus = ( 0.0, 0.0, 3.0,
                       0.0, 0.0, 0.0,
                       0.0, 1.0, 0.0 )
        self.zoom = 3.0

        # near, far clipping planes
        self.clip = ( 5.0, 5000.0 )

    def get_size( self ):
        """returns width, height of camera rendering area
        """
        rect = self.get_allocation()       
        return rect.width, rect.height

    def handle_init_gl( self ):
        """set up opengl lighting and such
        """
        light_ambient = (0.7, 0.7, 0.7, 1.0)
        light_diffuse = (1.0, 1.0, 1.0, 1.0)
        light_position = (10.0, 10.0, 10.0, 0.0)

        glLightfv(GL_LIGHT0, GL_AMBIENT, light_ambient)
        glLightfv(GL_LIGHT0, GL_DIFFUSE, light_diffuse)
        glLightfv(GL_LIGHT0, GL_POSITION, light_position)
        
        glEnable(GL_LIGHTING)
        glEnable(GL_LIGHT0)
        glEnable(GL_DEPTH_TEST)

        glShadeModel(GL_SMOOTH)
        glEnable(GL_AUTO_NORMAL)

        glClearColor(1.0, 1.0, 1.0, 1.0)
        glClearDepth(1.0)

        # set up texturing
        glEnable(GL_TEXTURE_2D)
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)

        self._set_view()
        
    def handle_draw( self ):
        """override to draw something
        """
        glMaterialfv( GL_FRONT, GL_SPECULAR, (1.0, 1.0, 1.0, 1.0) )
        glMaterialfv( GL_FRONT, GL_SHININESS, 100.0 )
        glMaterialfv( GL_FRONT, GL_DIFFUSE, (0.7, 0.0, 0.1, 1.0) )
        glutSolidTeapot( 10.0 )
 
    def handle_resize( self ):
        """do something when window is resized
        """
        pass

    def handle_motion( self, x, y ):
        """do something when mouse pointer is moved

           by default rotates view in x-y, override to change
        """
        if self.pointer_down:
            self.rotation[0] = x
            self.rotation[1] = y
            self.queue_draw()

    def handle_press( self, x, y ):
        """do something when pointer button is pressed
        """
        print "button pressed at %d, %d" % (x, y)

    def handle_release( self, x, y ):
        """do something when pointer button is released
        """
        pass

    ###
    ### private helper functions
    ###
            
    def _init_gl_widget( self ):
        # set opengl display mode
        # if creating a double buffered framebuffer fails try to create a
        # single buffered framebuffer
        display_mode = ( gtk.gdkgl.MODE_RGB |
                         gtk.gdkgl.MODE_DEPTH |
                         gtk.gdkgl.MODE_DOUBLE )
        glconfig = None
        try:
            glconfig = gtk.gdkgl.Config( mode=display_mode )
        except gdkgl.NoMatches:
            display_mode &= ~gtk.gdkgl.MODE_DOUBLE
            glconfig = gtk.gdkgl.Config( mode=mode )

        self.set_gl_capability( glconfig )

        self.set_events( gtk.gdk.POINTER_MOTION_MASK |
                         gtk.gdk.BUTTON_RELEASE_MASK |
                         gtk.gdk.BUTTON_PRESS_MASK )

    def _set_view( self ):
        width, height = self.get_size()

        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()

        # calculate left/right and top/bottom clipping planes based the
        # smallest square viewport
        a = self.zoom / min( width, height )
        clipping_planes = ( a * width, a * height )
        
        # setup the projection
        glFrustum(-clipping_planes[0], clipping_planes[0],
                  -clipping_planes[1], clipping_planes[1],
                  self.clip[0], self.clip[1] )
        
    ###
    ### private functions to map gtk events to canvas handlers
    ###

    def _on_realize( self, widget ):
        # call gl begin or die trying
        gl_context = self.get_gl_context()
        gl_drawable = self.get_gl_drawable()
        assert gl_drawable.gl_begin( gl_context ), \
               "couldn't gl begin in _on_realize()"
        
        try:
            # call gl init handler
            self.handle_init_gl()

        # call gl end
        finally:
            gl_drawable.gl_end()
        
    def _on_expose( self, gl_area, event ):
        # call gl begin or die trying
        gl_context = self.get_gl_context()
        gl_drawable = self.get_gl_drawable()
        assert gl_drawable.gl_begin( gl_context ), \
               "couldn't gl begin in _on_expose()"
        
        try:
            
            # ???
            glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

            # Set up the model view matrix
            glMatrixMode( GL_MODELVIEW )
            glLoadIdentity()

            gluLookAt( *self.focus )
            glTranslatef( *self.eye )

            glRotatef( self.rotation[0], 0.0, 1.0, 0.0 )
            glRotatef( self.rotation[1], 1.0, 0.0, 0.0 )
            glRotatef( self.rotation[2], 0.0, 0.0, 1.0 )

            # call draw handler to draw world
            self.handle_draw()


            # set view
            self._set_view()

            # swap or flush buffer
            if gl_drawable.is_double_buffered():
                gl_drawable.swap_buffers()
            else:
                glFlush()
                
        # call gl end
        finally:
            gl_drawable.gl_end()

        return True

    def _on_configure( self, gl_area, event ):
        # call gl begin or die trying
        gl_context = self.get_gl_context()
        gl_drawable = self.get_gl_drawable()
        assert gl_drawable.gl_begin( gl_context ), \
               "couldn't gl begin in _on_configure()"

        try:

            # resize gl viewport to fill camera window
            width, height = self.get_size()
            glViewport(0, 0, width, height)

            self._set_view()

            # call resize handler
            self.handle_resize()
            
        # OpenGL end
        finally:
            gl_drawable.gl_end()
            
        return True

    def _on_motion( self, drawing_area, event ):
        self.handle_motion( event.x, event.y )

    def _on_press( self, drawing_area, event ):
        self.pointer_down = True
        self.handle_press( event.x, event.y )

    def _on_release( self, drawing_area, event ):
        self.pointer_down = False
        self.handle_release( event.x, event.y )

    def _unthread_wrap( self, handler ):
        """wrap handlers to not automatically enter gtk thread lock
        """
        def wrapper( obj, *args ):
            gtk.gdk.threads_leave()
            handler( obj, *args )
            gtk.gdk.threads_enter()

        return wrapper

