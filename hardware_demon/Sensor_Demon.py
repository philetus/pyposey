import re
from threading import Thread
from pyxbee.Xbee import Xbee
from serial import SerialException

from pyposey.util.Log import Log

class Sensor_Demon( Thread ):
    """monitors serial xml stream and places couple events on sensor queue

       puts dict objects on sensor queue with these formats:
       {
           type:             "couple"
           
           hub_address:      (<high_byte>, <low_byte>)
           socket_index:     <0-3>

           strut_address:    (<high_byte>, <low_byte>) | None
           ball_index:       <0-1 | None>

           coupled_emitters: ( <0-10 | None>, <0-10 | None>,
                               <0-10 | None>, <0-10 | None> )
       }

       {
           type:             "accelerometer"

           hub_address:      (<high_byte>, <low_byte>)
           x:                <0-1024>
           y:                <0-1024>
           z:                <0-1024>
       }
           
    """
    LOG = Log( name='pyposey.hardware_demon.Sensor_Demon', level=Log.ERROR )
    
    TAG_PATTERN = re.compile( r'<([^<>]+)/>' )
    SOCKET_PATTERN = re.compile(
        r'socket_event\s+hub_address="([^"]+)"\s+'
        + r'socket="([^"]+)"\s+'
        + r'0="([^"]+)"\s+'
        + r'1="([^"]+)"\s+'
        + r'2="([^"]+)"\s+'
        + r'3="([^"]+)"\s+',
        re.I )
    ACCELEROMETER_PATTERN = re.compile(
        r'accelerometer_value\s+'
        + r'hub_address="([^"]+)"\s+'
        + r'x="([^"]+)"\s+'
        + r'y="([^"]+)"\s+'
        + r'z="([^"]+)"\s+',
        re.I )
    RN_PATTERN = re.compile( r'\r|\n' )

    SENSORS = 4 # sensors per socket
    EMITTERS = 11 # emitters per ball
    XML_BUFFER_SIZE = 4096 # max num characters to store in each xml buffer

    def __init__( self, sensor_queue=None, serial_port="/dev/ttyUSB0" ):
        """takes sensor queue to write to and xml stream to read from
        """
        Thread.__init__( self )

        # should only run until the thread that instantiated it stops
        self.setDaemon( True )

        self.sensor_queue = sensor_queue

        try:
          self.xbee = Xbee( port=serial_port, timeout=0.1 )
        except SerialException:
          print "ERROR: Unable to find USB base station; exiting."
          from sys import exit
          exit( -1 )


    def run( self ):
        """read text into buffer and parse it with regular expression
        """
        self.xbee.start()
        xml_buffer = {}
        
        while self.xbee.is_open():
            self.LOG.debug( "reading" )

            # block waiting for packet
            packet = self.xbee.read( timeout=None )
            address = tuple( packet.address )

            # create input stream for hub
            if not address in xml_buffer:
                xml_buffer[address] = ""

            # get data as string and append it to input stream
            string = packet.data
            string = string.replace( "\r", "" ) # no \r
            string = string.replace( "\n", "" ) # no \n
            xml_buffer[address] += string
            
            self.LOG.debug( "read: '%s'" % xml_buffer[address] )

            try:
                
                # if xml buffer has full tag parse it
                match = self.TAG_PATTERN.search( xml_buffer[address] )
                if match is not None:
                    self._parse_tag( match.group(1) )

                    # move to end of match
                    if match.start() > 0:
                        self.LOG.warn(
                            "unrecognized serial input: '%s'"
                            % xml_buffer[address][:match.start()] )
                    xml_buffer[address] = xml_buffer[address][match.end():]

                elif len(xml_buffer[address]) > self.XML_BUFFER_SIZE:
                    self.LOG.warn( "xml buffer overflow: %s"
                                   % xml_buffer[address] )
                    xml_buffer[address] = ""

            # recover from mangled tag
            except (ValueError, IndexError):
                self.LOG.warn(
                    "malformed tag: '%s'"
                    % xml_buffer[address][match.start():match.end()] )
                xml_buffer[address] = xml_buffer[address][match.end():]
                
        self.LOG.warn( "serial port closed!" )

    def _parse_tag( self, contents ):
        """parse event from contents of xml tag
        """
        # check if this is a connect event
        match = self.SOCKET_PATTERN.match( contents )
        if match is not None:

            # read hub and socket
            hub_address = self._parse_tuple( match.group(1) )
            socket = int( match.group(2) )

            # parse addresses and emitters
            strut_addresses = []
            emitters = []
            for i in range( 3, 7 ):
                raw = self._parse_tuple(match.group(i))
                address = raw[0], raw[1], raw[2] / self.EMITTERS
                emitter = raw[2] % self.EMITTERS
                if address[:2] == (0, 0):
                    strut_addresses.append( None )
                    emitters.append( None )
                else:
                    strut_addresses.append( address )
                    emitters.append( emitter )

            # check that all addresses that aren't none are the same
            address = None
            for a in strut_addresses:
                if a is not None:
                    if address is None:
                        address = a
                    else:
                        if a != address:
                            self.LOG.error(
                                "hub %s socket %d connected to multiple balls!"
                                % (str(hub_address), socket) )
                            raise ValueError()
                
            # create new couple event dict
            event = { "type":"couple" }
            
            # read hub data into couple event
            strut_address = (address[:2] if address is not None else None)
            ball = (address[2] if address is not None else None)
            event["hub_address"] = hub_address
            event["socket_index"] = socket
            event["strut_address"] = strut_address
            event["ball_index"] = ball
            event["coupled_emitters"] = tuple(emitters)

            if strut_address is None:
                self.LOG.info( "<%d.%d.%d x>"
                               % (event["hub_address"][0],
                                  event["hub_address"][1],
                                  event["socket_index"]) )
            else:
                emitlog = [ (str(v) if v is not None else "x")
                            for v in event["coupled_emitters"] ]
                self.LOG.info( "<%d.%d.%d %d.%d.%d %s %s %s %s>"
                               % (event["hub_address"][0],
                                  event["hub_address"][1],
                                  event["socket_index"],
                                  event["strut_address"][0],
                                  event["strut_address"][1],
                                  event["ball_index"],
                                  emitlog[0],
                                  emitlog[1],
                                  emitlog[2],
                                  emitlog[3]) )

            self.sensor_queue.put( event )
            return

        # check if this is an accelerometer value
        match = self.ACCELEROMETER_PATTERN.match( contents )
        if match is not None:

            # create new accelerometer event dict
            event = { "type":"accelerometer" }

            # read hub data into event
            event["hub_address"] = self._parse_tuple( match.group(1) )[:2]

            # read xyz values into event
            event["x"] = int( match.group(2), 16 )
            event["y"] = int( match.group(3), 16 )
            event["z"] = int( match.group(4), 16 )

            self.LOG.debug( "<%d.%d %d %d %d>" %
                           (event["hub_address"][0], event["hub_address"][1],
                            event["x"], event["y"], event["z"]) )

            self.sensor_queue.put( event )
            return

        self.LOG.warn( "unrecognized tag contents: %s" % contents )
                             

    def _parse_tuple( self, string ):
        """parse tuple from '.' separated ints: "32.9.7" -> (32, 9, 7)
        """
        return tuple( (int(i) for i in string.split(".")) )
