#
# script to print events parsed from xml and placed on queue by sensor demon
#

from Queue import Queue

from Sensor_Demon import Sensor_Demon

# create sensor queue
queue = Queue()

# create sensor demon
sensor_demon = Sensor_Demon( sensor_queue=queue, serial_port="/dev/ttyUSB0" )
sensor_demon.start()

accel_buffer = {}
accel_bundle = 5

couple_sets = set()
current_couples = { 0:None, 1:None, 2:None, 3:None }

def collect_couples():
    # read and print events from queue
    while queue is not None:
        event = queue.get( timeout=None )

        # check for connect event
        if event["type"] == "couple":

            # add current set to couple sets set
            sensor, emitter = event["sensor_index"], event["emitter_index"]
            if event["strut_address"] == (0, 0):
                emitter = None

            current_couples[sensor] = emitter

            couples = set()
            for sensor, emitter in current_couples.iteritems():
                if emitter is not None:
                    couples.add( (sensor, emitter) )

            couple_sets.add( frozenset(couples) )
            
            for i in range( 4 ):
                emitter = current_couples[i]
                if emitter == None:
                    emitter = "x"
                print "<%d %s>" % (i, str(emitter)),
            print "\n"

collect_couples()
