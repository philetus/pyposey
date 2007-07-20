from Molecule_Dictionary import Molecule_Dictionary

class Molecule_Matcher( object ):
    """matches molecules in a molecule dictionary against an atomic state

       maintains a set of molecules from the dictionary reachable from the
       current atomic state, and a set of molecules that have been constructed
    """
