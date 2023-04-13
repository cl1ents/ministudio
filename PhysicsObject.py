import pymunk

from pymunk import Body
from pygame import Vector2

class PhysicsObject:
    def __init__(self, app):
        self.body = pymunk.Body(1,1)
        self.app = app
        
    def update(self):
        pass
    
    def render(self):
        pass