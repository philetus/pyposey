from os import path
from Edited_Mesh import Edited_Mesh

###
### open a mesh
###

geometry_file = open( path.join("meshes", "bear_abdomen_b.txt"), "r" )
texture_file = open( path.join("meshes", "bear_torso_texture.png"), "rb" )


mesh = Edited_Mesh( geometry_file=geometry_file,
                    texture_file=texture_file,
                    translate=(0.0, 0.0, 0.0),
                    rotate=(0.0, 180.0, 0.0),
                    scale=(1.0, 1.0, 1.0) )

###
### calculate translation to center mesh bounding box
###

print "vertices:",
print len( mesh.vertices )

print "faces:",
print len( mesh.faces )

minv = [1000.0, 1000.0, 1000.0]
maxv = [-1000.0, -1000.0, -1000.0]

for v in mesh.vertices:
    for i in range( 3 ):
        if v[i] < minv[i]:
            minv[i] = v[i]
        if v[i] > maxv[i]:
            maxv[i] = v[i]

print "bounds:", minv, maxv

translate = [ (n + x) / -2.0 for n, x in zip(minv, maxv) ]
print "translate to centered:", translate

out_file = open( path.join( "meshes", "bear_abdomen_c.txt"), "w" )
mesh.write( out_file )
out_file.close()
