import re
from threading import Thread
from pyxbee.Xbee import Xbee
from serial import SerialException

from pyposey.util.Log import Log

class Sensor_Demon( Thread ):
    """monitors serial xml stream and places couple events on sensor queue

       puts dict objects on sensor queue with this format:
       {
           type:            "couple"
           
           hub_address:     (<high_byte>, <low_byte>)
           socket_index:    <0-3>
           sensor_index:    <0-3>

           strut_address:   (<high_byte>, <low_byte>)
           ball_index:      <0-1>
           emitter_index:   <0-10>
       }
           
    """
    LOG = Log( name='pyflexy.hardware_demon.Sensor_Demon', level=Log.WARN )
    
    TAG_PATTERN = re.compile( r'<([^<>]+)/>' )
    CONNECT_PATTERN = re.compile(
        r'connect_event\s+hub_address="([^"]+)"\s+'
        + r'strut_address="([^"]+)"\s+',
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
            string = "".join( chr(i) for i in packet.data )
            string = string.replace( "\r", "" ).replace( "\n", "" ) # no \r, \n
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
            except ValueError:
                self.LOG.warn(
                    "malformed tag: '%s'"
                    % xml_buffer[address][match.start():match.end()] )
                xml_buffer[address] = xml_buffer[address][match.end():]
                
        self.LOG.warn( "serial port closed!" )

    def _parse_tag( self, contents ):
        """parse event from contents of xml tag
        """
        # check if this is a connect event
        match = self.CONNECT_PATTERN.match( contents )
        if match is not None:
            
            # create new couple event dict
            event = { "type":"couple" }
            
            # read hub data into couple event
            raw = self._parse_tuple( match.group(1) )
            event["hub_address"] = raw[:-1]
            event["socket_index"] = raw[-1] / self.SENSORS
            event["sensor_index"] = raw[-1] % self.SENSORS

            # read strut data into couple event
            raw = self._parse_tuple( match.group(2) )
            event["strut_address"] = raw[:-1]
            event["ball_index"] = raw[-1] / self.EMITTERS
            event["emitter_index"] = raw[-1] % self.EMITTERS

            self.LOG.info( "<%d.%d.%d.%d %d.%d.%d.%d>"
                            % (event["hub_address"][0],
                               event["hub_address"][1],
                               event["socket_index"],
                               event["sensor_index"],
                               event["strut_address"][0],
                               event["strut_address"][1],
                               event["ball_index"],
                               event["emitter_index"]) )

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

            self.LOG.info( "<%d.%d %d %d %d>" %
                           (event["hub_address"][0], event["hub_address"][1],
                            event["x"], event["y"], event["z"]) )

            self.sensor_queue.put( event )
            return

        self.LOG.warn( "unrecognized tag contents: %s" % contents )
                             

    def _parse_tuple( self, string ):
        """parse tuple from '.' separated ints: "32.9.7" -> (32, 9, 7)
        """
        return tuple( (int(i) for i in string.split(".")) )
