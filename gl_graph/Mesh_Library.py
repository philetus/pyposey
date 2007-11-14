from xml import sax
from os import path
import re

from STL_Mesh import STL_Mesh
from Textured_Mesh import Textured_Mesh

class Mesh_Library( sax.handler.ContentHandler ):
    """library of stl meshes indexed by part type
    """

    LIST_PATTERN = re.compile( r'\),\s+\(' )
    
    def __init__( self, filename="mesh_library.xml", folder="meshes",
                  statusbar=True ):
        """
        """
        self.folder = folder
        self.statusbar = statusbar
        
        # dictionary of parts by address
        self.meshes = {}

        # open library file
        library_file = open( path.join(folder, filename) )
        if self.statusbar:
            print "meshes[",

        # parse xml file
        sax.parse( library_file, self )

        if self.statusbar:
            print "]"

        # close library file
        library_file.close()

    def __getitem__( self, key ):
        return self.meshes[key]

    def __iter__( self ):
        return self.meshes.itervalues()

    def startElement( self, name, attrs ):
        """parse data from part elements
        """
        if name == "mesh_library":
            pass
        elif name == "stl_mesh":
            self._build_stl_mesh( attrs )

        elif name == "textured_mesh":
            self._build_textured_mesh( attrs )
            
        else:
            raise ValueError( "unexpected tag in mesh library: '%s'!"
                              % mesh_name )

        if self.statusbar:
            print ">",

    def _build_stl_mesh( self, attrs ):
        """make new textured mesh using values in attributes dictionary
        """
        # get attributes
        args = {}
        args["name"] = str( attrs["name"] )
        args["part_type"] = str( attrs["part_type"] )
        stl_filename = str( attrs["stl_file"] )
        thumbnail_filename = str( attrs["thumbnail_file"] )
        args["specular"] = self._parse_floats( str(attrs["specular"]) )
        args["shininess"] = float( str(attrs["shininess"]) )
        args["diffuse"] = self._parse_floats( str(attrs["diffuse"]) )
        args["parent_angles"] = self._parse_float_lists(
            str(attrs["parent_angles"]) )
        args["parent_offsets"] = self._parse_floats(
            str(attrs["parent_offsets"]) )

        scale = self._parse_option( attrs, "scale" )
        if scale is not None:
            args["scale"] = scale
        if attrs.has_key( "flips" ):
            args["flips"] = float( attrs["flips"] )
        flip_axis = self._parse_option( attrs, "flip_axis" )
        if flip_axis is not None:
            args["flip_axis"] = flip_axis

        # try to open data files and create stl mesh object,
        # if mesh fails to load just print error message
        try:

            args["stl_file"] = open(
                path.join(self.folder, stl_filename), "rb" )
            args["thumbnail_file"] = open(
                path.join(self.folder, thumbnail_filename), "rb" )

            mesh = STL_Mesh( **args )
            
            args["thumbnail_file"].close()
            args["stl_file"].close()

            # add mesh to library using name as key
            if args["name"] in self.meshes:
                raise KeyError( "multiple meshes with name '%s'!"
                                % args["name"] )
            self.meshes[args["name"]] = mesh
       
        except Exception, error:
            print "failed to parse mesh named '%s': %s" % (
                attrs["name"], str(error) )

    def _build_textured_mesh( self, attrs ):
        args = {}
        # get attributes
        args["name"] = str( attrs["name"] )
        args["part_type"] = str( attrs["part_type"] )
        geometry_filename = str( attrs["geometry_file"] )
        texture_filename = str( attrs["texture_file"] )
        thumbnail_filename = str( attrs["thumbnail_file"] )
        args["parent_angles"] = self._parse_float_lists(
            str(attrs["parent_angles"]) )
        args["parent_offsets"] = self._parse_floats(
            str(attrs["parent_offsets"]) )

        scale = self._parse_option( attrs, "scale" )
        if scale is not None:
            args["scale"] = scale
        flips = None
        if attrs.has_key( "flips" ):
            args["flips"] = float( attrs["flips"] )
        flip_axis = self._parse_option( attrs, "flip_axis" )
        if flip_axis is not None:
            args["flip_axis"] = flip_axis

        # try to open data files and create textured mesh object,
        # if mesh fails to load just print error message
        try:
            args["geometry_file"] = open(
                path.join(self.folder, geometry_filename), "r" )
            args["texture_file"] = open(
                path.join(self.folder, texture_filename), "rb" )
            args["thumbnail_file"] = open(
                path.join(self.folder, thumbnail_filename), "rb" )
            
            mesh = Textured_Mesh( **args )

            # close files
            args["geometry_file"].close()
            args["texture_file"].close()
            args["thumbnail_file"].close()

            # add mesh to library using name as key
            if args["name"] in self.meshes:
                raise KeyError( "multiple meshes with name '%s'!"
                                % args["name"] )
            self.meshes[args["name"]] = mesh

        except Exception, error:
            print "failed to parse mesh named '%s': %s" % (
                attrs["name"], str(error) )

    def _parse_option( self, attrs, name ):
        if attrs.has_key( name ):
            return self._parse_floats( str(attrs[name]) )
        return None

    def _parse_float_lists( self, string ):
        raw_list = self.LIST_PATTERN.split( string[1:-1] )
        lists = []
        for s in raw_list:
            lists.append( tuple( float(i) for i in s.split( ", ") ) )
        return tuple( lists )
        
    def _parse_floats( self, string ):
        return tuple( float(s) for s in string.split(", ") )
    
