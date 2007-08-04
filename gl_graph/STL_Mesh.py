from struct import unpack
from OpenGL.GL import( glGenLists, glNewList, glEndList, glCallList,
                       glBegin, glEnd, glNormal3f, glVertex3f, glMaterialfv,
                       glPushMatrix, glPopMatrix,
                       GL_COMPILE, GL_TRIANGLES, GL_FRONT, GL_SPECULAR,
                       GL_SHININESS, GL_DIFFUSE )
from numpy import zeros
import gtk

class STL_Mesh( object ):
    """loads triangle mesh from an stl file and draws it with opengl calls
    """

    def __init__( self, name, part_type, stl_file, thumbnail_file,
                  specular, shininess, diffuse, parent_angles, parent_offsets,
                  scale=(1.0, 1.0, 1.0) ):
        self.name = name
        self.part_type = part_type
        
        self.triangles = None # list of triangles in mesh
        self.size = None # number of triangles in mesh
        self.list_name = None # gl display list name

        self.specular = specular
        self.shininess = shininess
        self.diffuse = diffuse

        self.parent_angles = parent_angles
        self.parent_offsets = parent_offsets

        # parse triangles from stl file
        self._parse_stl( stl_file, scale )

        # load thumbnail from thumbnail file
        self.thumbnail = None
        self._load_thumbnail( thumbnail_file )
        
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
        # preserve opengl settings
        glPushMatrix()
        
        if self.list_name is None:
            self._make_list()

        glCallList( self.list_name )

        # restore opengl settings
        glPopMatrix()

    def _parse_stl( self, stl_file, scale ):
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
                    self.triangles[i][j][k] = coords[k] * scale[k]
                    
            # read 2 byte int
            if unpack( "H", stl_file.read(2) )[0] != 0:
                print "non-zero attribute byte count at triangle %d: %d" % i

    def _load_thumbnail( self, thumbnail_file ):
        """load given thumbnail as gtk image
        """
        # silly hack to load gtk image from file object
        loader = gtk.gdk.PixbufLoader()
        loader.write( thumbnail_file.read() )
        loader.close()

        self.thumbnail = gtk.Image()
        self.thumbnail.set_from_pixbuf( loader.get_pixbuf() )


