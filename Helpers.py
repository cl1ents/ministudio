from Easing import *
from pygame import Vector2
from pygame import Rect

from math import hypot

def lerp(a, b, t, easing:EasingBase=LinearInOut):
    return a + (b - a) * easing.func(None, t)

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