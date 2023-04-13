from PhysicsObject import PhysicsObject
from Helpers import lerp, clamp, getPointAtAngle, addPoints
from Easing import CubicEaseInOut

from constants import *

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
        self.hoverboard.filter = pymunk.ShapeFilter(categories = PLAYER_CATEGORY)
        
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
        # self.body.velocity *= Vec2d(max(1-app.deltaTime, 0), 1)
        self.body.velocity += Vec2d(self.moveVector.x * 600 * 8 * app.deltaTime, 0)
        super().update()

    def hoverRay(self, origin):
        app = self.app

        target = getPointAtAngle(origin, -self.body.angle+math.pi, 50)

        eg = app.space.segment_query_first(origin, target, 1, pymunk.ShapeFilter())

        draw.line(app.screen, "Yellow", app.convertCoordinates(origin), app.convertCoordinates(target), 2)

    def render(self):
        super().render()
        app = self.app
        
        self.rect.center = app.convertCoordinates(self.body.position)
        self.image = pygame.transform.rotozoom(self.orig_image, math.degrees(self.body.angle), 1)
        
        self.rect = self.image.get_rect(center=self.rect.center)
        #print(self.rect)
        #draw.rect(app.screen, "Yellow", self.rect)
        app.screen.blit(self.image, self.rect)

        # Left ray
        self.hoverRay(getPointAtAngle(self.body.position, -self.body.angle-math.pi/2, 30))
        # Right ray
        self.hoverRay(getPointAtAngle(self.body.position, -self.body.angle+math.pi/2, 30))