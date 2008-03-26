from l33tC4D.vector.Vector3 import Vector3
from l33tC4D.vector.Matrix3 import Matrix3

def print_matrix( matrix ):
    for v in matrix:
        print "%.3f" % v,
    print "\n"

x = Vector3( (1, 0, 0) )
y = Vector3( (0, 1, 0) )
z = Vector3( (0, 0, 1) )

a = Vector3( (1, 0, 1) )

def strut_matrices():
    matrices = []
    for i in range( 2 ):
        matrices.append( Matrix3() )
    
    # rotate around y axis
    matrices[0].rotate( -90.0, y )
    matrices[1].rotate( 90.0, y )

    # translate distance to connector
    d = Vector3( z ).multiply( 71.5 )
    for m in matrices:
        m.translate( d )

    # fix this with mesh editor
    #matrices[0].rotate( -90.0, z )
    #matrices[1].rotate( 90.0, z )

    return matrices

def one_hub_matrix():
    matrix = Matrix3()

    matrix.rotate( 90.0, y )
        
    return matrix

def two_hub_matrices():
    matrices = []
    for i in range( 2 ):
        matrices.append( Matrix3() )

    for m in matrices:
        m.rotate( -90.0, y )
        
    matrices[1].rotate( 180.0, x )

    # translate distance to connector
    d = Vector3( z ).multiply( 53.0 )
    for m in matrices:
        m.translate( d )

    return matrices

def four_hub_matrices():
    matrices = []
    for i in range( 4 ):
        matrices.append( Matrix3() )

    # rotate around x axis
    for i, m in enumerate( matrices ):
        m.rotate( i * 90.0, x )

    # translate distance to connector
    d = Vector3( z ).multiply( 61.0 )
    for m in matrices:
        m.translate( d )

    return matrices

##for m in strut_matrices():
##    print_matrix( m )
print_matrix( one_hub_matrix() )
