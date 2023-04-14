import pymunk

from pymunk import Body
from pygame import Vector2

from Behaviour import Behaviour

class PhysicsObject(Behaviour):
    def __init__(self, app):
        self.body = pymunk.Body(1,1)
        self.app = app