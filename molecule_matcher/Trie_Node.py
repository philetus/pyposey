class Trie_Node( object ):
    """node in a molecule dictionary trie
    """

    def __init__( self ):
        self.symbol = None
        self.molecules = set() # molecules containing this trie node
        self.children = set() # children of this trie node
