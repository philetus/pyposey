from Queue import Queue

from Assembly_Demon import Assembly_Demon

class Fake_Queue( object ):
    def put( self, event ):
        print event
        
sensor_queue = Queue()
assembly_queue = Fake_Queue()

demon = Assembly_Demon( sensor_queue=sensor_queue,
                        assembly_queue=assembly_queue )

demon.start()
