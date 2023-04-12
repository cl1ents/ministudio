from Behaviour import Behaviour
from Helpers import lerp, raycast
from Easing import CubicEaseInOut

import pygame
import pygame.draw as draw
import pygame.transform as transform
from pygame import Vector2
from pygame import Rect

class Player(Behaviour):
    def __init__(self, app):
        super().__init__(app)
        self.position = Vector2(app.screenSize.x/2, app.screenSize.y/2)
    
    def update(self, app):
        self.velocity.y += 10 # lerp(Vector2(0, 0), Vector2(8, 2), (app.time % 2) / 2, CubicEaseInOut)

        cast = raycast(self.position, self.position+Vector2(0,100), [app.Baseplate.box])
        if cast:
            self.velocity.y -= (cast[1]-self.position.y)*.8
        #self.position.x = app.screenSize.x/2 + lerp(0, 400, (app.time%1)/1, QuadEaseOut)
        
        self.rotation = lerp(0, 360, (app.time%2)/2, CubicEaseInOut)
        
        super().update(app)
        pass

    def render(self, app):
        super().render(app)
        draw.circle(app.screen, "Red", self.position, 50)