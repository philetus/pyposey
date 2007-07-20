from logging import Logger, StreamHandler, Formatter
import sys

class Log( Logger, object ):
    """provides debugging and logging facilities
    """
    from logging import NOTSET, DEBUG, INFO, WARN, ERROR, CRITICAL

    def __init__( self, name, level=NOTSET ):
        """takes name of log and default log level
        """
        super( Log, self ).__init__( name=name, level=level )

        # handler to log messages to console
        self.console = StreamHandler( strm=sys.stderr )
        self.console.setFormatter(
            Formatter('%(name)-12s: %(levelname)-8s %(message)s') )
        self.addHandler( self.console )
       
