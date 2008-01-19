from Queue import Queue
from pyposey.assembly_graph.Part_Library import Part_Library
from pyposey.assembly_graph.Assembly_Graph import Assembly_Graph


# fake event queue
queue = Queue()

# load part library
library = Part_Library()

# start assembly graph
graph = Assembly_Graph( event_queue=queue, part_library=library )
graph.start()

def create( hub ):
    """queue a create event for given hub and strut addresses
    """
    queue.put({ "type":"create",
                "hub":hub })

def destroy( hub ):
    queue.put({ "type":"destroy",
                "hub":hub })
    
def connect( hub, strut ):
    """queue a connect event for given hub and strut addresses
    """
    queue.put({ "type":"connect",
                "hub":hub[:2],
                "socket":hub[2],
                "strut":strut[:2],
                "ball":strut[2] })

def disconnect( hub ):
    queue.put({ "type":"disconnect",
                "hub":hub[:2],
                "socket":hub[2] })

def find_intersections():
    
    # loop through subgraph parts sets
    for i in range( len(graph.subgraphs) - 1 ):
        parts = graph.subgraphs[i].parts

        for j in range( i + 1, len(graph.subgraphs) ):
            print "comparing subgraphs %d and %d ..." % (i, j),
            intersection = parts & graph.subgraphs[j].parts
            if intersection:
                print "intersection: %s!" % str(intersection)
            else:
                print "no intersection."

def stress():
    create( (42, 3) ) # one hub
    create( (88, 1) ) # four hub

    connect( (42, 3, 0), (3, 17, 0) )
    connect( (88, 1, 0), (3, 17, 1) )

    disconnect( (88, 1, 0) )
    connect( (88, 1, 1), (3, 17, 1) )

    create( (17, 4) )
    connect( (17, 4, 0), (3, 17, 1) )

        
