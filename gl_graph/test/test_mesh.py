from pyposey.gl_graph.Textured_Mesh import Textured_Mesh

###
### open a mesh
###

geometry_file = open( "meshes/bearx_mesh_5.txt", "r" )
texture_file = open( "meshes/bearx_head_texture.jpg", "rb" )
thumbnail_file = open( "meshes/bear_head_thumbnail.png", "rb" ) 
mesh = Textured_Mesh( name="bear head",
                      part_type="one hub",
                      geometry_file=geometry_file,
                      texture_file=texture_file,
                      thumbnail_file=thumbnail_file,
                      parent_angles="(0.0, 0.0, 0.0)",
                      parent_offsets="0.0" )

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

translate = [ (n + x) / -2.0 for n, x in zip(minv, maxv) ]
print translate
