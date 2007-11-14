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

# read and print events from queue
while queue is not None:
    event = queue.get()
    if event["emitter_index"] == 0:
        print "<%d.%d.%d.%d" % ( event["hub_address"][0],
                                 event["hub_address"][1],
                                 event["socket_index"],
                                 event["sensor_index"] ),
        if event["strut_address"] == (0, 0):
            print "x>"
        else:
            print "%d.%d.%d.%d>" % ( event["strut_address"][0],
                                     event["strut_address"][1],
                                     event["ball_index"],
                                     event["emitter_index"] )
