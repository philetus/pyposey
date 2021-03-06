from OpenGL.GL import *
from OpenGL.GLUT import *
import Image
import gtk
from math import *

class Textured_Mesh:
    """texture mapped model rendered in opengl

       reads in geometry data file output by yingdan's blender mesh
       geometry export script
    """

    MAX_BOUND = 1000.0

    def __init__( self, name, part_type, geometry_file, texture_file,
                  thumbnail_file, transforms,
                  flips=1, flip_axis=(0., 0., 1.) ):
        
        self.name = name
        self.part_type = part_type
        self.flips = flips
        self.flip_axis = flip_axis

        self.transforms = transforms
        
        self.centroid = None

        # seed bounds with max value
        self.bounds = [ [self.MAX_BOUND] * 3, [-self.MAX_BOUND] * 3 ]

        # extract vertices, faces and uv coords from geometry file
        self.vertices = None
        self.faces = None
        self.uv_coords = None
        self._extract_geometry( geometry_file )
        
        # load texture image from file
        self.texture_size = None
        self.texture = None
        self._load_texture_image( texture_file )
        
        # load thumbnail from thumbnail file
        self.thumbnail = None
        self._load_thumbnail( thumbnail_file )
        
        # opengl texture id and display list for textured mesh
        self.texture_id = None
        self.display_list = None

        self.diffuse = (1.0, 1.0, 1.0, 1.0)
        self.diffuse_selected = ( 0.8, 0.4, 0.1, 1.0 )
        

    def _extract_geometry( self, geometry_file ):
        """extract vertices, faces and uv coords from blender geometry file

           * vertices is a list of tuples of (x, y, z) coords
           * faces is a list of tuples of indices into the vertices list
             (v0, v1 ... vn) where n is 3 or 4
           * uv_coords is a tuple of (u, v) texture coord tuples for each vertex
             of each face
        """
        self.vertices = []
        self.faces = []
        self.uv_coords = []
        
        for line in geometry_file: #loop lines in the file
            line = line.split()
            if line[0] == "v":
                self._parse_vertex( line )
            elif line[0] == "f":
                self._parse_face( line )
            elif line[0] == "uv":
                self._parse_uv_coord( line )
        
    def _parse_vertex( self, line ):
        vertex = [ float(c) for c in line[1:] ]
        self.vertices.append( vertex )

        # update bounds to include this vertex's coords
        for i, coord in enumerate( vertex ):
            if coord < self.bounds[0][i]:
                self.bounds[0][i] = coord
            if coord > self.bounds[1][i]:
                self.bounds[1][i] = coord
            
    def _parse_face( self, line ):
        face = [ int(v) for v in line[1:] ]
        self.faces.append( face )

    def _parse_uv_coord( self, line ):
        uv_coord = [ [float(c) for c in line[i:i+2]]
                      for i in range(1, len(line), 2) ]
        self.uv_coords.append( uv_coord )

    def _load_texture_image( self, texture_file ):
        """load image from given texture file
        """
        image = Image.open( texture_file )
        self.texture_size = tuple( image.size )
        self.texture = image.tostring( "raw", "RGBX", 0, -1 )

    def _load_texture( self ):
        """load given texture file as an opengl texture
        """
        width, height = self.texture_size

        self.texture_id = glGenTextures( 1 )
        glBindTexture( GL_TEXTURE_2D, self.texture_id )
        glTexParameteri( GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR )
        glTexParameteri( GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR )
        glTexImage2D( GL_TEXTURE_2D, 0, GL_RGBA, width, height, 0, GL_RGBA,
                      GL_UNSIGNED_BYTE, self.texture )

    def _load_thumbnail( self, thumbnail_file ):
        """load given thumbnail as gtk image
        """
        # silly hack to load gtk image from file object
        loader = gtk.gdk.PixbufLoader()
        loader.write( thumbnail_file.read() )
        loader.close()

        self.thumbnail = gtk.Image()
        self.thumbnail.set_from_pixbuf( loader.get_pixbuf() )

    def _generate_display_list( self ):
        """generate opengl display list from geometry and texture files
        """
        if self.texture_id is None:
            self._load_texture()

        # create new display list
        self.display_list = glGenLists( 1 )
        glNewList( self.display_list, GL_COMPILE )
        # load texture map
        glBindTexture( GL_TEXTURE_2D, self.texture_id )
                
        # generate opengl calls for each face of the mesh
        for i, face in enumerate( self.faces ):
            face_vertices = [
                self.vertices[face[j] - 1] for j in range(len(face)) ]
            face_uv_coords = self.uv_coords[i]
            
            if len( face ) == 3:
                glBegin( GL_TRIANGLES )
            
            elif len( face ) == 4:
                glBegin(GL_QUADS)
                
            else:
                raise ValueError( "Can't generate textured mesh: "
                                  + "face must have 3 or 4 vertices!" )
            
            for j in range( len(face) ):          
                glTexCoord2f( *face_uv_coords[j] )
                glVertex3f( *face_vertices[j] )
                               
            glEnd()
        glEndList()

    def draw( self, selected=False ):
        """draw textured mesh to opengl by calling display list
        """        
        glEnable(GL_TEXTURE_2D)
        
        # preserve existing opengl settings
        glPushMatrix()
        
        # if display list has not been generated generate it
        if self.display_list is None:
            self._generate_display_list()

        # if mesh is selected use selected diffuse color
        if selected:
            glMaterialfv( GL_FRONT, GL_DIFFUSE, self.diffuse_selected )
        else:
            glMaterialfv( GL_FRONT, GL_DIFFUSE, self.diffuse )
 
        # call display list to draw mesh to screen
        glCallList( self.display_list )

        # restore opengl settings
        glPopMatrix()
        glDisable(GL_TEXTURE_2D)

        
