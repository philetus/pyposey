from threading import Thread
from Queue import Queue, Empty
from time import time

from pyposey.util.Log import Log

from Hub_Snitch import Hub_Snitch
from Polar_Couple_Map import Polar_Couple_Map

class Assembly_Demon( Thread ):
    """reads couple events from sensor queue and generates assembly events

       assembly demon that creates hub snitches as needed and passes
       assembly events to appropriate hub snitch which actually tracks socket
       state and generates assembly events

       assembly events are dicts with the following structure:

       create event - add new hub to assembly
       {
           type:    "create"
           hub:     ( <high_byte>, <low_byte> )
       }

       destroy event - remove hub from assembly
       {
           type:    "destroy"
           hub:     ( <high_byte>, <low_byte> )
       }

       connect event - connect socket of a hub to ball of a strut
       {
           type:    "connect"
           hub:     ( <high_byte>, <low_byte> )
           socket:  <0-3>
           strut:   ( <high_byte>, <low_byte> )
           ball:    <0-1>
       }

       disconnect event - remove strut from socket of a hub
       {
           type:    "disconnect"
           hub:     ( <high_byte>, <low_byte> )
           socket:  <0-3>
       }

       configure event - adjust the angle of the strut in a socket of a hub
       {
           type:    "configure"
           hub:     ( <high_byte>, <low_byte> )
           socket:  <0-3>
           strut:   ( <high_byte>, <low_byte> )
           ball:    <0-1>
           coords:     ( (<lon>, <lat>, <rot>) ... )           
       }

       up event - set accelerometer reading of up direction
       {
            type:    "up"
            hub:     ( <high_byte>, <low_byte> )
            x:       <float>
            y:       <float>
            z:       <float>
       }

    """
    LOG = Log( name='pyflexy.hardware_demon.Assembly_Demon', level=Log.INFO )

    TIMEOUT = 3.0
    
    def __init__( self, sensor_queue=None, assembly_queue=None ):
        Thread.__init__( self )

        # should only run until the thread that instantiated it stops
        self.setDaemon( True )

        self.sensor_queue = sensor_queue # queue to read couple events from
        self.assembly_queue = assembly_queue # queue to write assembly events to

        # dictionary of hubs by index
        self._snitches = {}

        # generate couple map
        self.couple_map = Polar_Couple_Map()

    def run( self ):
        """read events from sensor queue and farm them to hub demons
        """        
        while( self.sensor_queue and self.assembly_queue ):
            
            # block until an event is read from sensor queue
            event = self.sensor_queue.get()
            self.LOG.debug( "got sensor event %s" % str(event) )
            index = event["hub_address"]

            # if snitch doesn't exist create it
            if not self._snitches.has_key( index ):
                snitch = Hub_Snitch( index=index,
                                     queue=self.assembly_queue,
                                     couple_map=self.couple_map )
                self._snitches[index] = snitch

            # assign appropriate snitch to interpret event
            self._snitches[index].interpret( event )
                    
        self.LOG.debug( "no queue?" )
