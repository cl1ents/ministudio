from PhysicsObject import PhysicsObject
from Helpers import lerp, raycast, clamp
from Easing import CubicEaseInOut

import pygame
import pygame.draw as draw
import pygame.transform as transform
from pygame import Vector2
from pygame import Rect

import pymunk
from pymunk import Poly
from pymunk.vec2d import Vec2d

import math

class Player(PhysicsObject):
    def __init__(self, app):
        super().__init__(app)
        
        # Physics
        self.body.position = app.screenSize.x/2, app.screenSize.y/2
        self.body.mass = 1
        
        self.hoverboard = Poly.create_box(self.body, (100, 20))
        self.hoverboard.density = 0.1
        self.hoverboard.elasticity = 1
        self.hoverboard.friction = 0
        
        # Input
        self.jumpingCooldown = .1
        self.jumping = self.jumpingCooldown
        self.moveVector = Vector2(0,0)
        
        # Render
        self.image = pygame.Surface((100, 20), pygame.SRCALPHA)
        self.image.fill("Red")
        self.rect = self.image.get_rect(center=app.convertCoordinates(self.body.position))
        self.orig_image = self.image
        
        app.space.add(self.body, self.hoverboard)
    
    def jump(self):
        return
        if self.jumping > self.jumpingCooldown:
            self.jumping = 0

    def update(self):
        app = self.app
        # self.body.x += self.moveVector.x * clamp(600 - abs(self.velocity.x), 0, 600*8*app.deltaTime)
        #self.body.velocity += Vec2d(self.moveVector.x * clamp(600 - abs(self.body.velocity.x), 0, 600*8*app.deltaTime), 0)
        #self.body.velocity *= max(1-app.deltaTime, 0)
        self.body.velocity += Vec2d(self.moveVector.x * 600 * 8 * app.deltaTime, 0)
        super().update()

    def render(self):
        super().render()
        app = self.app
        
        self.rect.center = app.convertCoordinates(self.body.position)
        self.image = pygame.transform.rotozoom(self.orig_image, math.degrees(self.body.angle), 1)
        
        self.rect = self.image.get_rect(center=self.rect.center)
        #print(self.rect)
        #draw.rect(app.screen, "Yellow", self.rect)
        app.screen.blit(self.image, self.rect)