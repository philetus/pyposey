from xml import sax
from Hub import Hub
from Strut import Strut

class Part_Library( sax.handler.ContentHandler ):
    """library loads given hub and strut classes with data from a config file
    """
    STRUT_TYPES = set([ "strut" ])
    HUB_TYPES = set([ "one hub", "two hub", "three hub", "four hub" ])
    
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
                               part_type=part_type,
                               rootness=rootness,
                               label = label)
            self.parts[address] = part
            
        else:
            raise ValueError( "unexpected tag in mesh library: '%s'!"
                              % mesh_name )

    def _parse_address( self, string ):
        return tuple( int(s) for s in string.split(", ") )
