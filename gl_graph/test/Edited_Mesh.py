from OpenGL.GL import *
from OpenGL.GLUT import *
import Image
import gtk
from math import *

from l33tC4D.vector.Vector3 import Vector3
from l33tC4D.vector.matrices import( roll_pitch_yaw, scale_matrix,
                                     translate_matrix )

class Edited_Mesh:
    """texture mapped model rendered in opengl

       reads in geometry data file output by yingdan's blender mesh
       geometry export script
    """

    MAX_BOUND = 1000.0

    def __init__( self,
                  geometry_file,
                  texture_file,
                  translate=(0.0, 0.0, 0.0),
                  rotate=(0.0, 0.0, 0.0),
                  scale=(1.0, 1.0, 1.0) ):
        
        self.translate = translate_matrix( *translate )
        self.rotate = roll_pitch_yaw( *rotate )
        self.scale = scale_matrix( *scale )
        self.transform = self.scale * self.rotate * self.translate
        
        self.centroid = None

        self.name ="edited mesh"

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
        #print "vertex line:", line
        
        coords = [ float(c) for c in line[1:]]

        #print "coords:", coords
        
        # transform vertex by config transformation
        vertex = Vector3( *coords ).transform( self.transform )

        #print "vertex:", vertex, "\n"
        
        # append transformed vertex coords as a list
        self.vertices.append( list(vertex) )

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

    def draw( self, selected=False, flip=0 ):
        """draw textured mesh to opengl by calling display list
        """
        #print "drawing mesh %s ..." % self.name,

        try:
        
            glEnable(GL_TEXTURE_2D)
            # preserve existing opengl settings

            glPushMatrix()
            # if display list has not been generated generate it
            # or when press button again to flip the part with 90 degree
            if self.display_list is None or flip != self.flip:
                self._generate_display_list()
                self.flip = flip

            # print self.name, ": flip->", self.flip
            glRotatef( 90*self.flip , 0 , 1 , 0 ) 
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
            # self.flip = (self.flip+1)%4

        except Exception, error:
            print "error: %s", str( error ),

        #print "finished drawing"

    def write( self, out ):
        """
        """
        # write vertices to file
        for v in self.vertices:
            out.write( "v %.5f %.5f %.5f\n" % tuple(v) )

        # write out faces and uv coords
        for face, uv_coords in zip( self.faces, self.uv_coords ):

            # write out vertices for face
            out.write( "f" )
            for v in face:
                out.write( " %d" % v )
            out.write( "\n" )

            # write out uv coords for face
            out.write( "uv" )
            for pair in uv_coords:
                for c in pair:
                    out.write( " %.5f" % c )
            out.write( "\n" )
