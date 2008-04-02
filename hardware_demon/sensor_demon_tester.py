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
accel_bundle = 1

# read and print events from queue
while queue is not None:
    event = queue.get()

    # check for connect event
    if event["type"] == "couple":
        emitters = list( event["coupled_emitters"] )
        if 0 in emitters:
            print "<%d.%d>" % (event["socket_index"], emitters.index(0))
        else:
            print "<%d.x>" % event["socket_index"]

    elif event["type"] == "accelerometer":
        address = event["hub_address"]
        
        if address not in accel_buffer:
            accel_buffer[address] = [0, 0, 0, 0]

        accel_buffer[address][-1] += 1 # increment bundle counter

        for i, c in enumerate( ["x", "y", "z"] ):
            accel_buffer[address][i] += event[c]

        if accel_buffer[address][-1] >= accel_bundle:
            values = tuple( i / accel_bundle
                            for i in accel_buffer[address][:-1] )
            print "<%d.%d %d %d %d>" % (address + values)

            accel_buffer[address] = [0, 0, 0, 0]
        
