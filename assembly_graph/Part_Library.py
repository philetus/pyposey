from xml import sax
import re
from Hub import Hub
from Strut import Strut

class Part_Library( sax.handler.ContentHandler ):
    """library loads given hub and strut classes with data from a config file
    """
    STRUT_TYPES = set([ "strut" ])
    HUB_TYPES = set([ "one hub", "two hub", "three hub", "four hub" ])
    LIST_PATTERN = re.compile( r'\(([\d\.\-\s]+)\)' )
    
    def __init__( self, hub_class=Hub, strut_class=Strut,
                  filename="part_library.xml" ):
        """
        """
        # dictionary of parts by address
        self.parts = {}

        self.hub_class = hub_class
        self.strut_class = strut_class

        # open library file
        library_file = open( filename )

        # parse xml file
        sax.parse( library_file, self )

        # close library file
        library_file.close()

    def __contains__( self, key ):
        return self.parts.__contains__( key )

    def __getitem__( self, key ):
        return self.parts[key]

    def __iter__( self ):
        return self.parts.itervalues()

    def startElement( self, name, attrs ):
        """parse data from part elements
        """
        if name == "part_library":
            pass
        elif name == "part":
            
            # get attributes
            address = self._parse_address( str(attrs["address"]) )
            children = int( str(attrs["children"]) )
            part_type = str( attrs["part_type"] )
            rootness = float( str(attrs["rootness"]) )
            label = "x"
            if attrs.has_key( "label" ):
                label = str(attrs["label"])
            transforms = None
            if attrs.has_key( "transforms" ):
                transforms = self._parse_float_lists( str(attrs["transforms"]) )
            
            # generate part and add it to dictionary by address
            part_class = None
            if part_type in self.STRUT_TYPES:
                part_class = self.strut_class
            elif part_type in self.HUB_TYPES:
                part_class = self.hub_class
            else:
                raise ValueError( "unexpected part type: '%s'!" % part_type )
                
            part = part_class( address=address,
                               children=children,
                               transforms=transforms,
                               part_type=part_type,
                               rootness=rootness,
                               label = label )
            self.parts[address] = part
            
        else:
            raise ValueError( "unexpected tag in mesh library: '%s'!"
                              % mesh_name )

    def _parse_address( self, string ):
        return tuple( int(s) for s in string.split(", ") )

    def _parse_float_lists( self, string ):
        """parse lol from string formatted as "(1.0 0.0 1.0) (0.0 0.0 3.0) ..."
        """
        float_lists = []
        for match in self.LIST_PATTERN.finditer( string ):
            l = [ float(s) for s in match.group(1).split() ]
            float_lists.append( l )
        return float_lists
