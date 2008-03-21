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

m = Matrix3()
#n = Matrix3()

m.rotate( 180.0, x )
#m.rotate( 180.0, z )

# rotate around y axis
#m.rotate( 0.0, y )
#m.rotate( -90.0, y )

# translate distance to connector
#d = Vector3( z ).multiply( 71.5 )
#m.translate( d )
#n.translate( d )

# rotate 90 degrees around z axis
#m.rotate( 90.0, z )
#n.rotate( -90.0, z )

print_matrix( m )
#print_matrix( n )
