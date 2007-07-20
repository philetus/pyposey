from pyflexy.util.Xmlizable import Xmlizable
from pyflexy.util.Log import Log

from Bond import Bond

class Atom( Xmlizable ):
    """a node in a graph of bonded atoms
    """

    LOG = Log( "pyflexy.molecule_matcher.Atom", Log.DEBUG )
    
    def __init__( self, address=None, symbol=None, name=None, bonds=0 ):
        self.address = address
        self.symbol = symbol
        self.name = name
        self.bonds = [None] * bonds

    def __repr__( self ):
        return '<atom symbol="%s" address="%s" />' % (
            self.symbol, ".".join([str(i) for i in self.address]) )

##
## xml sax event handling methods required to implement Xmlizable interface
##

    def start_xml( self, attrs ):
        """start parsing atom data from xml tag
        """
        self.name = str( attrs['name'] )
        self.symbol = str( attrs['symbol'] )
        self.address = tuple( [int(s) for s in attrs['address'].split(".")] )
        self.bonds = [None] * int( attrs['bonds'] )

    def start_child_element( self, name, attrs ):
        """handle beginning child element xml tag
        """
        if name == "bond":
            number = int( attrs["number"] )
            address = tuple( [int(s) for s in attrs["address"].split(".")] )
            self.bonds[number] = Bond( address=address )
            
        else:
            self.LOG.warn( "unexpected start tag for %s" % name )

    def end_child_element( self, name ):
        """handle ending child element xml tag
        """
        if name != "bond":
            self.LOG.warn( "unexpected end tag for %s" % name )

    def finish_xml( self ):
        """finish parsing atom info from xml tag
        """
        pass
