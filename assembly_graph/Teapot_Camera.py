from OpenGL.GLUT import glutSolidTeapot

from GLUT_Camera import GLUT_Camera

class Teapot_Camera( GLUT_Camera ):
    """test app opens a camera window and draws a teapot
    """

    def __init__( self ):
        GLUT_Camera.__init__( self )

    def handle_draw( self ):
        """draw a teapot
        """
        glutSolidTeapot( 10 )

    def handle_press( self, x, y ):
        """
        """
        print "button pressed at %d, %d" % (x, y)

if __name__ == "__main__":
    camera = Teapot_Camera()
    camera.show()
