import gtk
import gtk.gtkgl
from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *

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

        # width and height
        self.width = 1
        self.height = 1

        # for rotating view
        self.rotation = 0.0

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

    def select( self, x, y, box=(2, 2), buffer_size=512 ):
        """returns list of gl names of objects at given screen coords

           gl names are ordered from nearest to furthest
        """
        select_buffer = None
        
        # call gl begin or die trying
        gl_context = self.get_gl_context()
        gl_drawable = self.get_gl_drawable()
        assert gl_drawable.gl_begin( gl_context ), \
               "couldn't gl begin in _on_expose()"
        
        try:
            # set up pick matrix
            glMatrixMode( GL_PROJECTION )
            glLoadIdentity()
            gluPickMatrix( x, y, box[0], box[1],
                           (0, 0, self.width, self.height) )

            # set projection view but don't clear pick matrix
            self._set_projection_view( init=False )

            # init selection render mode
            glInitNames()
            glSelectBuffer( buffer_size )
            glRenderMode( GL_SELECT )

            # set model view
            self._set_model_view()

            # draw objects to selection buffer
            self.handle_draw()

            # get list of names and restore render mode
            glFlush()
            select_buffer = glRenderMode( GL_RENDER )
            
        finally:
            gl_drawable.gl_end()

        return self._sort_gl_names( select_buffer )
        

    def handle_init_gl( self ):
        """set up opengl lighting and such
        """
        """
        light_ambient = (0.2, 0.2, 0.2, 1.0)
        light_diffuse = (1.0, 1.0, 1.0, 1.0)
        light_position = (0.0, 300.0, 300.0, 0.0)

        glLightfv(GL_LIGHT0, GL_AMBIENT, light_ambient)
        glLightfv(GL_LIGHT0, GL_DIFFUSE, light_diffuse)
        glLightfv(GL_LIGHT0, GL_POSITION, light_position)
        
        glEnable(GL_LIGHTING)
        glEnable(GL_LIGHT0)
        """
        white2 = (0.2, 0.2, 0.2, 1.0)
        white6 = (0.6, 0.6, 0.6, 1.0)
        white = (1.0, 1.0, 1.0, 1.0)
        black = (0.0, 0.0, 0.0, 1.0)

        mat_shininess = (50.0)

        light0_position = (6000.0, 4000.0, 5000.0, 0.0)
        light1_position = (-6000.0, -4000.0, 5000.0, 0.0)
        light2_position = (6000.0, 4000.0, -5000.0, 0.0)
        light3_position = (-6000.0, -4000.0, -5000.0, 0.0)
        
        glLightfv(GL_LIGHT0, GL_POSITION, light0_position)
        glLightfv(GL_LIGHT0, GL_AMBIENT, black)
        glLightfv(GL_LIGHT0, GL_DIFFUSE, white)
        glLightfv(GL_LIGHT0, GL_SPECULAR, white)
        glEnable(GL_LIGHT0)

        glLightfv(GL_LIGHT1, GL_POSITION, light1_position)
        glLightfv(GL_LIGHT1, GL_AMBIENT, black)
        glLightfv(GL_LIGHT1, GL_DIFFUSE, white)
        glLightfv(GL_LIGHT1, GL_SPECULAR, white)
        glEnable(GL_LIGHT1)

        glLightfv(GL_LIGHT2, GL_POSITION, light2_position)
        glLightfv(GL_LIGHT2, GL_AMBIENT, black)
        glLightfv(GL_LIGHT2, GL_DIFFUSE, white)
        glLightfv(GL_LIGHT2, GL_SPECULAR, white)
        glEnable(GL_LIGHT2)

        glLightfv(GL_LIGHT3, GL_POSITION, light3_position)
        glLightfv(GL_LIGHT3, GL_AMBIENT, black)
        glLightfv(GL_LIGHT3, GL_DIFFUSE, white)
        glLightfv(GL_LIGHT3, GL_SPECULAR, white)
        glEnable(GL_LIGHT3)
        glEnable(GL_LIGHTING)

        glEnable(GL_NORMALIZE)
        # glEnable(GL_COLOR_MATERIAL)
        glEnable(GL_DEPTH_TEST)
        glShadeModel(GL_SMOOTH)
        glEnable(GL_AUTO_NORMAL)

        glClearColor(1.0, 1.0, 1.0, 1.0)
        glClearDepth(1.0)

        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)

        
    def handle_draw( self ):
        """override to draw something besides a teapot
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
            self.rotation = x
            self.queue_draw()

    def handle_press( self, x, y ):
        """do something when pointer button is pressed
        """
        print "button presse at %d, %d" % (x, y)
        print self.select( x, y )

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

    def _set_projection_view( self, init=True ):
        """set up perspective view matrix
        """
        # if init is set go into projection matrix mode and clear matrix
        if init:
            glMatrixMode(GL_PROJECTION)
            glLoadIdentity()

        # calculate left/right and top/bottom clipping planes based the
        # smallest square viewport
        a = self.zoom / min( self.width, self.height )
        clipping_planes = ( a * self.width, a * self.height )
        
        # setup the projection
        glFrustum(-clipping_planes[0], clipping_planes[0],
                  -clipping_planes[1], clipping_planes[1],
                  self.clip[0], self.clip[1] )

    def _set_model_view( self, init=True ):
        """set up model view matrix
        """
        # if init arg is set go into model view matrix mode and clear matrix
        if init:
            # Set up the model view matrix
            glMatrixMode( GL_MODELVIEW )
            glLoadIdentity()

        gluLookAt( *self.focus )
        glTranslatef( *self.eye )

        # rotate coord frame so +z is up and +x is right
        glRotatef( -90.0, 1.0, 0.0, 0.0 )

        # rotate around z axis with mouse x
        glRotatef( self.rotation, 0.0, 0.0, 1.0 )
            
    ###
    ### private functions to map gtk events to canvas handlers
    ###
    
    def _on_realize( self, widget ):
        """Called by GTK when widget is displayed on screen
        """
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
        """Called by GTK to redraw widget
        """
        # call gl begin or die trying
        gl_context = self.get_gl_context()
        gl_drawable = self.get_gl_drawable()
        assert gl_drawable.gl_begin( gl_context ), \
               "couldn't gl begin in _on_expose()"
        
        try:
            
            # ???
            glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

            # set up projection view matrix
            self._set_projection_view()

            # set up the model view matrix
            self._set_model_view()

            # call draw handler to draw world
            self.handle_draw()

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
            self.width, self.height = self.get_size()
            glViewport( 0, 0, self.width, self.height )

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
        self.handle_press( event.x, self.height - event.y )

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

    def _sort_gl_names( self, select_buffer ):
        """sort top names from each name stack by minimum depth, near to far
        """
        # put names in dictionary by minimum depth
        names_by_depth = {}
        for selection in select_buffer:
            names_by_depth[selection[0]] = selection[-1][-1]

        # add to list by depth
        depths = names_by_depth.keys()
        depths.sort()
        names = []
        for depth in depths:
            names.append( int(names_by_depth[depth]) )

        return names
