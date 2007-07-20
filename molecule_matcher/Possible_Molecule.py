
class Possible_Molecule( object ):
    """a construction of atoms presenting several possible molecules
    """

    def __init__( self ):
        # free atoms 
        self.atoms = {} # self.atoms[symbol, index] = atom
        self.fragments = [] # list of fragments sorted by size

    def add_atom( self, atom ):
        """add new atom to possible molecule
        """
        # add atom to atoms dictionary
        self.atoms[atom.symbol, atom.index]  = atom

        # add to prefix and suffix possible molecules
        for child in self.prefix, self.suffix:
            child.add_atom( atom )

    def remove_atom( self, atom ):
        """remove existing atom from possible molecule
        """
        # remove atom from atoms dictionary
        del self.atoms[atom.symbol, atom.index]

        # remove from prefix and suffix possible molecules
        for child in self.prefix, self.suffix:
            child.remove_atom( self, atom )

    def add_bond( self, *atoms ):
        """create a bond between two given atoms
        """
        atoms[0].bonds.add( atoms[1].symbol, atoms[1].index )
        atoms[1].bonds.add( atoms[0].symbol, atoms[0].index )

    def remove_bond( self, *atoms ):
        """remove bond between two given atoms
        """
        atoms[0].bonds.remove( atoms[1].symbol, atoms[1].index )
        atoms[1].bonds.remove( atoms[0].symbol, atoms[0].index )
    
