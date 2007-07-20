from time import sleep

from l33tgui.Gui import Gui
from l33tgui.Canvas import Canvas
from l33tgui.Circle import Circle

from Couple_Map import Couple_Map

class Couple_Map_Canvas( Canvas ):
    """test app to visualize couple map results
    """

    def __init__( self, gui, granularity=10 ):
        super( Couple_Map_Canvas, self ).__init__( gui=gui )

        self.map = Couple_Map( granularity )
        self.circles = [] # list of circles to draw
        self.color = ( 1.0, 0.0, 1.0, 0.6 )
        self.background_color = ( 1.0, 1.0, 1.0, 1.0 ) # opaque white

        self.size = (400, 400)

        # set window title
        self.title = "couple map canvas"

    def handle_draw( self, brush ):
        """when a canvas redraw is triggered draw all lines in the lines list
           and if we are in the middle of drawing a line draw rubber band
        """
        # draw background
        brush.color = self.background_color
        width, height = self.size
        brush.move_to( 0, 0 )
        brush.path_to( width, 0 )
        brush.path_to( width, height )
        brush.path_to( 0, height )
        brush.close_path()
        brush.fill_path()
        brush.clear_path()
        
        # draw all circles in lines list
        for circle in self.circles:
            circle.draw( brush )

    def set_couples( self, *couples ):
        """generate circles to draw from list of couples
        """
        self.circles = []

        for roll, pitch, yaw in self.map.couples[frozenset(couples)]:

            circle = Circle( (200 + yaw, 200 + pitch), (roll + 190) / 10 )
            self.circles.append( circle )

        self.redraw()

    def slideshow( self, seconds=2 ):
        """give a slideshow of possible couples and their ranges
        """
        couples = [ tuple(key) for key in self.map.couples.iterkeys() ]
        couples.sort()

        for i in range( len(couples) ):
            print i, couples[i]
            canvas.set_couples( *couples[i] )
            sleep( seconds )

if __name__ == "__main__":
    gui = Gui()
    gui.start()
    
    canvas = Couple_Map_Canvas( gui )
    canvas.show()

    canvas.slideshow()        
