class Atom_Set( dict ):
    """holds sets of atoms of different types

       an atom set is a superset of another atom set if it has at least as
       many of every kind of atom that the other atom set has
    """

    def __repr__( self ):
        string = "<atom set "
        for symbol in sorted( self.iterkeys() ):
            string += "%s:%d " % ( symbol, len(self[symbol]) )
        string += "/>"
        return string

    def add( self, atom ):
        """add given atom to this atom set by symbol
        """
        if not self.has_key( atom.symbol ):
            self[atom.symbol] = set()
        self[atom.symbol].add( atom )

    def remove( self, atom ):
        """remove given atom from this atom set
        """
        self[atom.symbol].remove( atom )
        if len( self[atom.symbol] ) < 1:
            del self[atom.symbol]

    def issubset( self, atom_set ):
        """returns true if given atom set contains the same # or more of every
           atom contained by this atom set
        """
        for symbol in self.iterkeys():
            try:
                if len( self[symbol] ) > len( atom_set[symbol] ):
                    return False
            except KeyError:
                return False

            return True

    def issuperset( self, atom_set ):
        """returns true if this atom contains as many of every type of atom
           as the given atom set
        """
        return atom_set.issubset( self )

    def __iter__( self ):
        """iterate over all of the atoms in this atom set
        """
        for _set in self.itervalues():
            for atom in _set:
                yield atom

    def __contains__( self, atom ):
        """return true if given atom is contained by this atom set
        """
        for _set in self.itervalues():
            if atom in _set:
                return True

        return False
