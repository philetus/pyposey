from xml import sax

class Xmlizable( object ):
    """abstract class for objects to be generated from xml
    """        

    def parse_xml_file( self, xml_file, root_tag ):
        """parse elements from this element down from file
        """
        # create temporary xmlizable attributes and redirect
        # start element and end element calls to this object
        self._xmlizable_end_tag = root_tag
        self._xmlizable_handler = sax.handler.ContentHandler()
        self._xmlizable_handler.startElement = self._handle_start_element
        self._xmlizable_handler.endElement = self._handle_end_element

        # parse file with redirected handler
        sax.parse( xml_file, self._xmlizable_handler )

        # delete temporary attributes when finished
        del self._xmlizable_end_tag
        del self._xmlizable_handler

    def read_xml( self, parent, name, attrs ):
        """set this object's start_element and end_element methods
           to receive sax events until closing tag
        """
        # set temporary xmlizable attributes
        self._xmlizable_parent = parent
        self._xmlizable_handler = parent._xmlizable_handler
        self._xmlizable_end_tag = name

        # update handlers
        self._xmlizable_handler.startElement = self.start_child_element
        self._xmlizable_handler.endElement = self._handle_end_element

        # start xml parsing
        self.start_xml( attrs )

    def _handle_start_element( self, name, attrs ):
        """look for opening document tag
        """
        if name == self._xmlizable_end_tag:
            self._xmlizable_handler.startElement = self.start_child_element
            self.start_xml( attrs=attrs )

        else:
            raise Xmlizable_Error( "document root tag preceded by %s" % name )

    def _handle_end_element( self, name ):
        """return control to parent xml element
        """
        # if this is not end tag for element call end child element method
        if self._xmlizable_end_tag != name:
            self.end_child_element( name )
            return
        
        # otherwise call finish xml method and return sax handler control
        # to parent
        self.finish_xml()

        # if this is the top level element just return
        if not hasattr( self, "_xmlizable_parent" ):
            return

        parent = self._xmlizable_parent
        handler = self._xmlizable_handler
        handler.startElement = parent.start_child_element
        handler.endElement = parent._handle_end_element
        del self._xmlizable_end_tag
        del self._xmlizable_handler
        del self._xmlizable_parent

        parent.end_child_element( name=name )

    @staticmethod
    def indent_string( string ):
        """indent each line in string by a single tab
        """
        return ''.join([ '\t' + line + '\n' for line
                         in str.splitlines(string) ])

    def start_xml( self, attrs ):
        """called by read_xml with xml attributes of corresponding tag
        """
        raise NotImplementedError()

    def start_child_element( self, name, attrs ):
        """handle child sax tags to generate this object
        """
        raise NotImplementedError()

    def end__child_element( self, name ):
        """handle sax child ending tag
        """
        raise NotImplementedError()

    def finish_xml( self ):
        """called when this object's closing tag is reached
        """
        raise NotImplementedError()

    def xmlize( self ):
        """return string containing xmlized object
        """
        raise NotImplementedError()

