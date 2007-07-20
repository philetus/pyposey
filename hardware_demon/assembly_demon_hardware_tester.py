from Queue import Queue

from Sensor_Demon import Sensor_Demon
from Assembly_Demon import Assembly_Demon

class Fake_Queue( object ):
    def put( self, event ):
        print event
        
sensor_queue = Queue()
assembly_queue = Fake_Queue()

sensor_demon = Sensor_Demon( sensor_queue=sensor_queue )

assembly_demon = Assembly_Demon( sensor_queue=sensor_queue,
                        assembly_queue=assembly_queue )

sensor_demon.start()
assembly_demon.start()
