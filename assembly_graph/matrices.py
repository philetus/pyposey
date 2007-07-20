from numpy import matrix
from math import sqrt, radians, cos, sin

def angle_axis( angle, u, v, w ):
    """builds a 4d numpy matrix to rotate angle degrees around given axis

       angle - angle to rotate in degrees
    """
    ###
    ### from http://www.mines.edu/~gmurray/ArbitraryAxisRotation/ArbitraryAxisRotation.html
    ###
    c = cos( radians(angle) )
    s = sin( radians(angle) )
    t = 1 - c
    u2, v2, w2 = u**2, v**2, w**2
    d = u2 + v2 + w2
    root = sqrt( d )
    
    # generate rotation matrix
    return matrix(
        [[(u2+((v2+w2)*c))/d, (u*v*t-w*root*s)/d, (u*w*t+v*root*s)/d, 0],
         [(u*v*t+w*root*s)/d, (v2+((u2+w2)*c))/d, (v*w*t-u*root*s)/d, 0],
         [(u*w*t-v*root*s)/d, (v*w*t+u*root*s)/d, (w2+((u2+v2)*c))/d, 0],
         [0, 0, 0, 1]],
        'd' )

def roll( angle ):
    """builds 4d numpy matrix for rotation about x axis
    """
    angle = radians( float(angle) )
    c = cos( angle )
    s = sin( angle )
    return matrix(
        [[1, 0, 0, 0],
         [0, c, s, 0],
         [0, -s, c, 0],
         [0, 0, 0, 1]],
        'd' )

def pitch( angle ):
    """builds 4d numpy matrix for rotation about y axis
    """
    angle = radians( float(angle) )
    c = cos( angle )
    s = sin( angle )
    return matrix(
        [[c, 0, -s, 0],
         [0, 1, 0, 0],
         [s, 0, c, 0],
         [0, 0, 0, 1]],
        'd' )

def yaw( angle ):
    """builds 4d numpy matrix for rotation about z axis
    """
    angle = radians( float(angle) )
    c = cos( angle )
    s = sin( angle )
    return matrix(
        [[c, s, 0, 0],
         [-s, c, 0, 0],
         [0, 0, 1, 0],
         [0, 0, 0, 1]],
        'd' )
