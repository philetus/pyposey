from OpenGL.GL import( glTranslatef, glRotatef, glMultMatrixf,
                       glPushMatrix, glPopMatrix )
                       
from l33tC4D.vector.Vector3 import Vector3
from l33tC4D.vector.matrices import pitch, yaw, yaw_pitch_roll

from pyposey.util.Log import Log

from GLUT_Camera import GLUT_Camera
from STL_Mesh import STL_Mesh

class Graph_Camera( GLUT_Camera ):
    """renders assembly graph with opengl
    """
    LOG = Log( name='pyposey.assembly_graph.Graph_Camera', level=Log.INFO )

    ROOT_OFFSET = (200., 0., 0.)
    ROTATION_AXIS = (0., 0., 1.)

    def __init__( self, assembly_graph, title="Flexy Assembly Viewer" ):
        """viewer constructor takes gui and queue to read events from
        """
        GLUT_Camera.__init__( self, title=title )

        # assembly graph to render
        self.graph = assembly_graph

        # set up assembly graph to call redraw on change
        self.graph.observers.append( self.redraw )

        # load stl meshes
        print "meshes[",
        
        self.strut_mesh = STL_Mesh( "graphics_strut.stl" )
        self.strut_mesh.diffuse = STL_Mesh.GREY

        print ">",
        
        self.hub_meshes = {}
        
        self.hub_meshes[1] = STL_Mesh( "graphics_one_hub.stl" )
        self.hub_meshes[1].diffuse = STL_Mesh.YELLOW

        print ">",

        self.hub_meshes[4] = STL_Mesh( "graphics_four_hub.stl" )
        self.hub_meshes[4].diffuse = STL_Mesh.BLUE

        print "]"

        # nodes visited during rendering
        self.visited = None

        # eye point for view
        self.eye = ( 0.0, 0.0, -2000.0 )

    def handle_draw( self ):
        """traverse graph and draw hubs and struts
        """
        # acquire assembly graph lock before traversing graph
        self.graph.lock.acquire()
        try:

            for hub in self.graph.roots:

                # remember this spot
                glPushMatrix()

                # build up
                glRotatef( 90.0, *self.ROTATION_AXIS )

                # init visited set
                self.visited = set()

                # visit hub and render its graph
                try:
                    self._visit_hub( hub )
                except Exception, error:
                    self.LOG.error( error )

                # clear visited set
                self.visited = None

                # come back
                glPopMatrix()
        
                # translate by offset coords
                glTranslatef( *self.ROOT_OFFSET )

        finally:
            self.graph.lock.release()

    def _visit_hub( self, hub ):
        """draw hub and visit its children
        """
        # add to visited set
        self.visited.add( hub )
        
        # render hub
        self.hub_meshes[len(hub.sockets)].draw()

        # visit children
        for socket in hub.sockets:
            ball = socket.ball
            if (ball is not None) and (ball.strut not in self.visited):

                # remember this spot
                glPushMatrix()

                # move to socket
                glRotatef( socket.parent_angle, *self.ROTATION_AXIS )
                glTranslatef( socket.parent_offset, 0., 0. )

                # set roll, pitch and yaw
                r, p, y = [ sum(_range) / 2. for _range in socket.angle ]

                # rotate into strut
                self._rotate_in( r, p, y )

                # move to strut
                glTranslatef( ball.parent_offset, 0., 0. )
                glRotatef( 180. - ball.parent_angle, *self.ROTATION_AXIS )
                glRotatef( ball.parent_roll, 1.0, 0.0, 0.0 )

                # visit strut
                self._visit_strut( ball.strut )

                # come back
                glPopMatrix()

    def _visit_strut( self, strut ):
        """draw strut and visit its children
        """
        # add to visited set
        self.visited.add( strut )

        # render strut
        self.strut_mesh.draw()

        # visit children
        for ball in strut.balls:
            socket = ball.socket
            if (socket is not None) and (socket.hub not in self.visited):

                # remember this spot
                glPushMatrix()

                # move to ball
                glRotatef( ball.parent_angle, *self.ROTATION_AXIS )
                glTranslatef( ball.parent_offset, 0., 0. )
                glRotatef( ball.parent_roll, 1.0, 0.0, 0.0 )

                # yaw, pitch and roll back to socket orientation
                r, p, y = [ sum(_range) / 2. for _range in socket.angle ]

                # rotate out of strut
                self._rotate_out( r, p, y )

                # move to hub
                glTranslatef( socket.parent_offset, 0., 0. )
                glRotatef( 180.0 - socket.parent_angle, *self.ROTATION_AXIS )

                # visit hub
                self._visit_hub( socket.hub )

                # come back
                glPopMatrix()

    def _rotate_in( self, r, p, y ):
        angle = None
        axis = None
        
        if p == 0.0 and y == 0.0:
            angle = 0.0
            axis = (1.0, 0.0, 0.0)

        else:
            old = Vector3( 1.0, 0.0, 0.0 )
            new = old.transform( yaw(-y) * pitch(-p) )

            angle = old.angle_to( new )
            axis_vector = old.cross( new ).normalize()
            axis = tuple( axis_vector )

        self.LOG.debug( "rpy (%f, %f, %f) to angle %f axis %s"
                        % (r, p, y, angle, str(axis)) )
                
        glRotatef( angle, *axis )
        glRotatef( -r, 1.0, 0.0, 0.0 )

        
    def _rotate_out( self, r, p, y ):
        angle = None
        axis = None
        
        if p == 0.0 and y == 0.0:
            angle = 0.0
            axis = (1.0, 0.0, 0.0)

        else:
            old = Vector3( 1.0, 0.0, 0.0 )
            new = old.transform( yaw(y) * pitch(-p) )

            angle = new.angle_to( old )
            axis_vector = new.cross( old ).normalize()
            axis = tuple( axis_vector )

        glRotatef( angle, *axis )
        glRotatef( -r, 1.0, 0.0, 0.0 )
