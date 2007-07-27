class Assembly_Subgraph:
    """subgraph of connected parts
    """

    def __init__( self ):
        self.root = None
        self.parts = set()

    def __len__( self ):
        return len( self.parts )

    def add( self, part ):
        """add new part to subgraph
        """
        # add part to parts set
        self.parts.add( part )

        # set this subgraph as part subgraph
        if part.subgraph is not None:
            part.subgraph.remove( part )
        part.subgraph = self

        # check if this part should be root
        if self.root is None or part.rootness > self.root.rootness:
            self.root = part

    def remove( self, part ):
        """remove part from subgraph
        """
        assert part.subgraph is self
        part.subgraph = None
        self.parts.discard( part )

        # if part was root pick new root
        if self.root is part:
            self.root = None
            self._pick_root()

    def _pick_root( self ):
        """make part with highest rootness root
        """
        for part in self.parts:
            if self.root is None or part.rootness > self.root.rootness:
                self.root = part

    def pop( self ):
        return self.parts.pop()
