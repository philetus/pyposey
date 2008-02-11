from l33tC4D.vector.Matrix3 import Matrix3

class Node:
    """superclass for hub and strut graph nodes
    """

    def __init__( self, address, children, child_class, **args ):
        self.address = address
        self.rootness = args["rootness"] if "rootness" in args else None
        self.label = args["label"] if "label" in args else None
        self.type = args["part_type"] if "part_type" in args else None

        # list of transforms for each child
        transforms = (args["transforms"] if
                      ("transforms" in args and args["transforms"] is not None)
                      else [ None ] * children)
        assert len(transforms) == children

        # matrix to track orientation
        self.orientation = Matrix3()

        # current subgraph of assembly graph
        self.subgraph = None

        # build list of children
        self.children = []
        for i in range( children ):
            child = child_class( parent=self, index=i, transform=transforms[i] )
            self.children.append( child )


    def __getitem__( self, key ):
        return self.children[key]

    def __iter__( self ):
        for child in self.children:
            yield child

    def __len__( self ):
        return len( self.children )

    def get_connected( self ):
        """returns set of nodes connected to this node
        """
        connected = set()
        for child in self.children:
            if child.connected is not None:
                connected.add( child.connected.parent )
                
        return connected

    def translate( self, vector3 ):
        """translate node by given vector
        """
        self.orientation.translate( vector3 )

    def rotate( self, degrees, axis ):
        """rotate node around given axis
        """
        self.orientation.rotate( degrees, axis )

    def transform( self, matrix3 ):
        """transform node by given matrix
        """
        self.orientation *= matrix3

    def align( self, node=None ):
        """reset orientation to align with given node
        """
        self.orientation = ( Matrix3(node.orientation) if node is not None
                             else Matrix3() )
    

    def _get_position( self ):
        return self.orientation.position

    position = property( fget=_get_position,
                         doc="current (x, y, z) position of node" )
