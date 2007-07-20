import sys
from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *

class GLUT_Camera( object ):
    """a window showing a view of an opengl world
    """
        
    def __init__( self, title="GLUT Camera", size=(800, 600) ):
        self.title = title
        self.size = size

        self.running = False
        
        # last mouse coords
        self.pointer = [ 0, 0 ]

        # eye position and focus
        self.eye = ( 0.0, 0.0, -6.0 )

        # near, far clipping planes
        self.clip = ( 50, 5000 )


        # light
        self.lights = [ {}, {} ]
	self.lights[0]["diffuse"] = (0.99, 0.99, 0.99, 1.0)
        self.lights[0]["position"] = (40.0, 40, 100.0, 0.0)
	self.lights[1]["diffuse"] = (0.99, 0.99, 0.99, 1.0)
        self.lights[1]["position"] = (-40.0, 40, 100.0, 0.0)

    def show( self ):
        # set running flag
        self.running = True
        
        glutInit( sys.argv )

        # create window with glut calls
	glutInitDisplayMode( GLUT_RGBA | GLUT_DOUBLE | GLUT_ALPHA | GLUT_DEPTH )      
        glutInitWindowSize( *self.size )
        glutCreateWindow( self.title )
        
        # setup the callbacks
        glutDisplayFunc( self._on_display )
        glutMotionFunc( self._on_motion )
        glutReshapeFunc( self._on_reshape )
        glutIdleFunc( self._on_idle )

        # ???
        glClearDepth( 1.0 )
        glClearColor( 0.0, 0.0, 0.0, 0.0 )
        glShadeModel( GL_SMOOTH )

	# setup lights
        glLightfv( GL_LIGHT0, GL_DIFFUSE, self.lights[0]["diffuse"] )
        glLightfv( GL_LIGHT0, GL_POSITION, self.lights[0]["position"] )
	glEnable( GL_LIGHT0 )
        glLightfv( GL_LIGHT1, GL_DIFFUSE, self.lights[1]["diffuse"] )
        glLightfv( GL_LIGHT1, GL_POSITION, self.lights[1]["position"] )
	glEnable( GL_LIGHT1 )
	glEnable( GL_LIGHTING )

        # ???
	glEnable( GL_DEPTH_TEST )
	glEnable( GL_AUTO_NORMAL )
	glEnable( GL_NORMALIZE )

        # start main loop
        glutMainLoop()

    def redraw( self ):
        """manually trigger a canvas redraw event
        """
        if self.running:
            glutPostRedisplay()
        else:
            print "glut camera not running yet!"

    def handle_draw( self ):
        """draw something
        """
        raise NotImplementedError( "Don't you want to draw something?" )
 
    def handle_resize( self ):
        """do something when window is resized
        """
        pass

    def handle_motion( self, x, y ):
        """do something when mouse pointer is moved
        """
        pass

    def handle_press( self, x, y ):
        """do something when pointer button is pressed
        """
        pass

    def handle_release( self, x, y ):
        """do something when pointer button is released
        """
        pass

    ###
    ### private functions to map gtk events to canvas handlers
    ###
        
    def _on_display( self ):
            
        # clear the buffer
        glClear( GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT )

        # Set up the model view matrix
        glMatrixMode( GL_MODELVIEW )
        glLoadIdentity()
        glTranslatef( *self.eye )
        glRotatef( self.pointer[0], 0.0, 1.0, 0.0 )
        glRotatef( self.pointer[1], 1.0, 0.0, 0.0 )

        # call draw handler to draw world
        self.handle_draw()

        # swap buffer
        glutSwapBuffers()

    def _on_reshape( self, width, height ):
        # setup the viewport
        glViewport( 0, 0, width, height )
        
        # setup the projection matrix
        glMatrixMode( GL_PROJECTION )
        glLoadIdentity()
        
        # calculate left/right and top/bottom clipping planes based the
        # smallest square viewport
        a = 9.0 / min( width, height )
        clipping_planes = ( a*width, a*height )
        
        # setup the projection
        glFrustum(-clipping_planes[0], clipping_planes[0],
                  -clipping_planes[1], clipping_planes[1],
                  self.clip[0], self.clip[1] )

    def _on_idle( self ):
        pass

    def _on_motion( self, x, y ):
        self.pointer[0] = x
        self.pointer[1] = y

        glutPostRedisplay()

    def _on_press( self, drawing_area, event ):
        self.handle_press( event.x, event.y )

    def _on_release( self, drawing_area, event ):
        self.handle_release( event.x, event.y )
    
