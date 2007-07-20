from pyflexy.util.Xmlizable import Xmlizable

from Molecule import Molecule

class Molecule_Dictionary( dict, Xmlizable ):
    """dictionary that reads list of molecules from an xml file
    """

    def parse( self, xml_file ):
        """parse molecule dictionary from xml file
        """
        self.parse_xml_file( xml_file=xml_file, root_tag="molecule_dictionary" )

    ###
    ### implement xmlizable sax interface
    ###

    def start_xml( self, attrs ):
        """called for opening root document xml tag
        """
        print "started processing molecule dictionary xml"

    def start_child_element( self, name, attrs ):
        """handle sax start element events
        """
        # create a new molecule for each molecule tag
        if name == "molecule":
            self._temp_molecule = Molecule()
            self._temp_molecule.read_xml( parent=self, name=name, attrs=attrs )

        else:
            print "hub molecule: unexpected start tag for %s" % name            

    def end_child_element( self, name ):
        """handle sax end element events
        """
        if name == "molecule":

            # put temp molecule into dictionary by symbol
            self[self._temp_molecule.symbol] = self._temp_molecule

            # delete temporary reference
            del self._temp_molecule
                
        else:
            print "hub molecule: unexpected end tag for %s" % name

    def finish_xml( self ):
        """called for closing root document xml tag
        """
        print "finished processing molecule dictionary xml"

    ###
    ### xmlizable xml writer function
    ###

    def xmlize( self ):
        """return xml object as a string
        """
        string = "<molecule_dictionary>\n"

        symbols = list( self.iterkeys() )
        symbols.sort()
        for symbol in symbols:
            string += self.indent_string( self[symbol].xmlize() )

        string += "</molecule_dictionary>\n"

        return string
