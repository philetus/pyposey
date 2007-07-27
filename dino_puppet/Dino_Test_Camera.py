from OpenGL.GL import *

from GLUT_Camera import GLUT_Camera

from STL_Mesh import STL_Mesh

class Mesh_Camera( GLUT_Camera ):
    """test app opens gl camera window and draws stl mesh
    """

    def __init__( self ):
        GLUT_Camera.__init__( self )
        
        self.one_hub_mesh = STL_Mesh( "mm_dinosaur_right_foot.stl" )
        self.one_hub_mesh.diffuse = STL_Mesh.GREEN

        self.two_hub_mesh = STL_Mesh( "solid_two_hub.stl" )
        self.two_hub_mesh.diffuse = STL_Mesh.GREEN

        self.four_hub_mesh = STL_Mesh( "mm_dinosaur_body.stl" )
        self.four_hub_mesh.diffuse = STL_Mesh.GREEN

        self.strut_mesh = STL_Mesh( "mm_dinosaur_right_leg.stl" )
        self.strut_mesh.diffuse = STL_Mesh.GREEN

        self.eye = ( 0.0, 0.0, -1500.0 )

    def handle_draw( self ):
        """draw stl mesh
        """
        # rotate hub 45 degrees
        glRotatef( 45.0, 0.0, 1.0, 0.0 )

        self.four_hub_mesh.draw()

        # draw strut
        glPushMatrix()
        glTranslatef( 58.30, 0.0, 0.0 )
        self.strut_mesh.draw()
        glTranslatef( 125.77, 0.0, 0.0 )
        self.one_hub_mesh.draw()
        glPopMatrix()

        # draw another
        glPushMatrix()
        glRotatef( 90.0, 0.0, 1.0, 0.0 )
        glTranslatef( 58.30, 0.0, 0.0 )
        self.strut_mesh.draw()
        glPopMatrix()

        #print "handle draw 1"

    def handle_press( self, x, y ):
        """
        """
        print "button pressed at %d, %d" % (x, y)

if __name__ == "__main__":
    camera = Mesh_Camera()
    camera.show()
