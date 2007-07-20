from pyflexy.util.Xmlizable import Xmlizable

from Atom import Atom
from Atom_Set import Atom_Set

class Molecule( Xmlizable ):
    """a graph of bonded atoms
    """

    def __init__( self ):
        self.name = None
        self.symbol = None
        self.atom_set = Atom_Set()

    def __repr__( self ):
        return '<molecule symbol="%s" name="%s" />' % (self.symbol, self.name)

##
## xml sax event handling methods required to implement Xmlizable interface
##

    def start_xml( self, attrs ):
        """start parsing hub data from xml tag
        """
        self.name = str( attrs['name'] )
        self.symbol = str( attrs['symbol'] )

    def start_child_element( self, name, attrs ):
        """handle beginning child element xml tag
        """
        if name == "atom":

            # create new atom
            self._temp_atom = Atom()

            # redirect sax events to socket
            self._temp_atom.read_xml( parent=self, name=name, attrs=attrs )

        else:
            print "molecule: unexpected start tag for %s" % name

    def end_child_element( self, name ):
        """handle ending child element xml tag
        """
        if name == "atom":

            # place atom in atoms data structure
            self.atom_set.add( self._temp_atom )

            # delete temp atom reference
            del self._temp_atom

        else:
            print "molecule: unexpected end tag for %s" % name

    def finish_xml( self ):
        """finish parsing molecule info from xml tag
        """
        # merge atomic bonds
        bonds = {}
        for atom in self.atom_set:
            for bond in atom.bonds:
                if bond is not None:

                    # if bond address not already in dictionary add it
                    if not bonds.has_key( bond.address ):
                        bonds[bond.address] = bond
                        bond.atom_set.add( atom )

                    # otherwise replace this bond with existing
                    atom.bonds[atom.bonds.index(bond)] = bonds[bond.address]
                    bonds[bond.address].atom_set.add( atom )

##
## xmlizable output method
##
    def xmlize( self ):
        """return string containing xmlized molecule
        """
        string = '<molecule symbol="%s" name="%s">\n' % (
            self.symbol, self.name )
        for atom in self.iter_atoms():
            string += self.indent_string( atom.xmlize() )
        string += "</molecule>\n"
        return string

    
