from easing_functions import *
from pygame import Vector2
from pygame import Rect
from pymunk import Vec2d

import math

def lerp(a, b, t, easing=LinearInOut):
    return a + (b - a) * easing.func(None, t)

def clamp(num, min_value, max_value):
   return max(min(num, max_value), min_value)

def clamp01(num):
    return clamp(num, 0, 1)

def reflect(inDirection:Vec2d, inNormal:Vec2d):
    return -2 * inNormal.dot(inDirection) * inNormal + inDirection

""" Old raycasting!
def raycast(origin: Vector2, target: Vector2, collisions: list, maxsteps=10):
    casting = True
    
    boundingBox = collisions[0]
    if len(collisions) > 1:
        boundingBox = Rect.unionall(*collisions)
    innerRay = Rect.clipline(boundingBox, origin, target)

    if innerRay:
        intersection = innerRay[0]
        dist = hypot(intersection[0]-origin.x, intersection[1]-origin.y)
        for collision in collisions:
            ray = Rect.clipline(boundingBox, innerRay)[0]
            currdist = hypot(ray[0]-origin.x, ray[1]-origin.y)
            if currdist < dist:
                intersection = ray
                dist = currdist
        return intersection
"""

def addPoints(a, b):
    return (a[0]+b[0], a[1]+b[1])

def getPointAtAngle(point=(0,0), angle=0, distance=1):
    return addPoints(point, (math.sin(angle)*distance, math.cos(angle)*distance))