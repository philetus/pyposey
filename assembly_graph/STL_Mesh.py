from struct import unpack
from OpenGL.GL import( glGenLists, glNewList, glEndList, glCallList,
                       glBegin, glEnd, glNormal3f, glVertex3f, glMaterialfv,
                       GL_COMPILE, GL_TRIANGLES, GL_FRONT, GL_SPECULAR,
                       GL_SHININESS, GL_DIFFUSE )
from Numeric import zeros

class STL_Mesh( object ):
    """loads triangle mesh from an stl file and draws it with opengl calls
    """

    # diffuse colors
    RED = ( 0.7, 0.0, 0.1, 1.0 )
    GREEN = ( 0.0, 0.7, 0.1, 1.0 )
    BLUE = ( 0.0, 0.1, 0.7, 1.0 )
    YELLOW = ( 0.7, 0.8, 0.1, 1.0 )
    GREY = ( 0.4, 0.4, 0.5, 1.0 )

    def __init__( self, stl_filename ):
        self.triangles = None # list of triangles in mesh
        self.size = None # number of triangles in mesh
        self.list_name = None # gl display list name

        self.specular = ( 1.0, 1.0, 1.0, 1.0 )
        self.shininess = 100.0
        self.diffuse = self.RED

        # open stl file and parse triangles
        stl_file = None
        try:
            stl_file = open( stl_filename, 'rb' )
            self._parse_stl( stl_file )
        finally:
            stl_file.close()

    def _make_list( self ):
        """generate opengl display list to draw triangles in mesh
        """
        # get available list name
        self.list_name = glGenLists( 1 )

        # start new display list
        glNewList( self.list_name, GL_COMPILE )

        # set material
        glMaterialfv( GL_FRONT, GL_SPECULAR, self.specular )
	glMaterialfv( GL_FRONT, GL_SHININESS, self.shininess )
        glMaterialfv( GL_FRONT, GL_DIFFUSE, self.diffuse )
        
        # start list of triangles in mesh
        glBegin( GL_TRIANGLES )

        # for each triangle give normal and 3 vertices
        for triangle in self.triangles:
            glNormal3f( *triangle[0] )
            for i in range( 1, 4 ):
                glVertex3f( *triangle[i] )
        
        glEnd()
        glEndList()

    def draw( self ):
        """draw stl mesh by executing opengl display list
        """
        if self.list_name is None:
            self._make_list()

        glCallList( self.list_name )

    def _parse_stl( self, stl_file ):
        """parse triangles from stl file
        """
        # skip header
        stl_file.seek( 80 )

        # read number triangles
        self.size = unpack( "I", stl_file.read(4) )[0]

        # make array to hold triangle data
        self.triangles = zeros( (self.size, 4, 3), 'd' )

        # read triangles
        for i in range( self.size ):

            # read normal and vertex coords for triangle
            for j in range( 4 ):
                coords = unpack( "fff", stl_file.read(12) )
                for k in range( 3 ):
                    self.triangles[i][j][k] = coords[k]                

            # read 2 byte int
            if unpack( "H", stl_file.read(2) )[0] != 0:
                print "non-zero attribute byte count at triangle %d: %d" % i
