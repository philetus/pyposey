from OpenGL.GL import( glTranslatef, glRotatef, glMultMatrixf,
                       glPushMatrix, glPopMatrix )
                       
from GLUT_Camera import GLUT_Camera
from STL_Mesh import STL_Mesh
from l33tC4D.vector.matrices import pitch_yaw_roll, yaw_pitch_roll

class Dino_Camera( GLUT_Camera ):
    """renders assembly graph with opengl
    """

    ROOT_OFFSET = (200., 0., 0.)
    ROTATION_AXIS = (0., 1., 0.)

    def __init__( self, assembly_graph, title="Flexy Assembly Viewer" ):
        """viewer constructor takes gui and queue to read events from
        """
        GLUT_Camera.__init__( self, title=title )

        # assembly graph to render
        self.graph = assembly_graph

        # set up assembly graph to call redraw on change
        self.graph.observers.append( self.redraw )

        # load stl meshes
        self.meshes = {}

        self.meshes[(42,2)] = STL_Mesh( "mm_dinosaur_left_foot.stl" )
        self.meshes[(42,2)].diffuse = STL_Mesh.GREEN

        self.meshes[(42,3)] = STL_Mesh( "mm_dinosaur_right_foot.stl" )
        self.meshes[(42,3)].diffuse = STL_Mesh.GREEN

        self.meshes[(42,4)] = STL_Mesh( "mm_dinosaur_head.stl" )
        self.meshes[(42,4)].diffuse = STL_Mesh.GREEN

        self.meshes[(42,5)] = STL_Mesh( "mm_dinosaur_head.stl" )
        self.meshes[(42,5)].diffuse = STL_Mesh.GREEN

        self.meshes[(88,1)] = STL_Mesh( "mm_dinosaur_body.stl" )
        self.meshes[(88,1)].diffuse = STL_Mesh.GREEN

        self.meshes[(3,17)] = STL_Mesh( "mm_dinosaur_neck.stl" )
        self.meshes[(3,17)].diffuse = STL_Mesh.GREEN
        
        self.meshes[(3,18)] = STL_Mesh( "mm_dinosaur_tail.stl" )
        self.meshes[(3,18)].diffuse = STL_Mesh.GREEN

        self.meshes[(3,19)] = STL_Mesh( "mm_dinosaur_left_leg.stl" )
        self.meshes[(3,19)].diffuse = STL_Mesh.GREEN

        self.meshes[(3,20)] = STL_Mesh( "mm_dinosaur_right_leg.stl" )
        self.meshes[(3,20)].diffuse = STL_Mesh.GREEN

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
                self._visit_hub( hub )

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
        self.meshes[hub.number].draw()

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
                angle = [ sum(_range) / 2. for _range in socket.angle ]
                angle[1], angle[2] = angle[2], angle[1] # switch y and z
                matrix = pitch_yaw_roll( *angle )
                glMultMatrixf( tuple(matrix.flat) )

                # move to strut
                glTranslatef( ball.parent_offset, 0., 0. )
                glRotatef( 180. - ball.parent_angle, *self.ROTATION_AXIS )

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
        self.meshes[strut.number].draw()

        # visit children
        for ball in strut.balls:
            socket = ball.socket
            if (socket is not None) and (socket.hub not in self.visited):

                # remember this spot
                glPushMatrix()

                # move to ball
                glRotatef( ball.parent_angle, *self.ROTATION_AXIS )
                glTranslatef( ball.parent_offset, 0., 0. )

                # yaw, pitch and roll back to socket orientation
                angle = [ sum(_range) / 2. for _range in socket.angle ]
                angle[1], angle[2] = angle[2], angle[1] # switch y and z
                matrix = yaw_pitch_roll( *angle )
                glMultMatrixf( tuple(matrix.flat) )

                # move to hub
                glTranslatef( socket.parent_offset, 0., 0. )
                glRotatef( 180.0 - socket.parent_angle, *self.ROTATION_AXIS )

                # visit hub
                self._visit_hub( socket.hub )

                # come back
                glPopMatrix()
