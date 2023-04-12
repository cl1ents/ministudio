from Behaviour import Behaviour
from Helpers import lerp, raycast, clamp
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

        self.jumpingCooldown = .1
        self.jumping = self.jumpingCooldown
        self.moveVector = Vector2(0,0)
    
    def jump(self):
        if self.jumping > self.jumpingCooldown:
            self.jumping = 0

    def setMoveVector(self, moveVector):
        self.moveVector = moveVector

    def update(self, app):
        self.velocity.y += 10

        cast = raycast(self.position, self.position+Vector2(0,100), [app.Baseplate.box])

        if self.jumping == 0 and cast: # Jump
            self.velocity.y = min(self.velocity.y, 20)
            self.velocity.y -= 500
        elif cast and self.jumping > self.jumpingCooldown: # Stick to ground
            self.velocity.y -= self.position.y-(cast[1]-75)
        elif cast: # DONT STICK TO GROUND! Push back.
            self.velocity.y -= 100-(cast[1]-self.position.y)
        
        if self.jumping < self.jumpingCooldown:
            print(self.jumping)

        self.velocity.x += self.moveVector.x * clamp(600 - abs(self.velocity.x), 0, 600*8*app.deltaTime)

        #self.position.x = app.screenSize.x/2 + lerp(0, 400, (app.time%1)/1, QuadEaseOut)
        
        self.rotation = lerp(0, 360, (app.time%2)/2, CubicEaseInOut)
        
        self.jumping += app.deltaTime
        super().update(app)
        pass

    def render(self, app):
        super().render(app)
        draw.circle(app.screen, "Red", self.position, 50)