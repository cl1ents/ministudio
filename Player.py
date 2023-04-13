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
    mask = pymunk.ShapeFilter(mask=pymunk.ShapeFilter.ALL_MASKS()^PLAYER_CATEGORY)

    def __init__(self, app):
        super().__init__(app)
        
        # Physics
        self.body.position = app.screenSize.x/2, app.screenSize.y/2
        self.body.mass = 1
        
        self.hoverboard = Poly.create_box(self.body, (100, 20))
        self.hoverboard.density = 0.3
        self.hoverboard.elasticity = 1
        self.hoverboard.friction = 1
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
        if self.jumping > self.jumpingCooldown:
            self.jumping = 0

    def update(self):
        app = self.app
        
        

        # Left ray
        left = self.hoverRay(Vec2d(-30,0), 100-(abs(clamp(self.moveVector.x, -1, 0)))*10)# getPointAtAngle(self.body.position, -self.body.angle-math.pi/2, 30))
        # Right ray
        right = self.hoverRay(Vec2d(30,0), 100-(abs(clamp(self.moveVector.x, 0, 1)))*10)
    
        floor = left or right
        if self.jumping == 0 and floor:
            self.body.apply_impulse_at_local_point((0,500000))
        if floor and self.jumping > self.jumpingCooldown: # Stick to floor
            self.body.apply_impulse_at_local_point((self.moveVector.x*8000, 0))
        else:
            self.body.angular_velocity += -self.moveVector.x*app.deltaTime*50

        self.jumping += app.deltaTime
        super().update()

    def hoverRay(self, offset, dist=100):
        app = self.app

        origin = self.body.local_to_world(offset)
        target = self.body.local_to_world(Vec2d(offset.x, -dist))

        seg = app.space.segment_query_first(origin, target, 1, self.mask)

        if seg:
            currentVel = self.body.world_to_local(origin+self.body.velocity_at_local_point(offset))
            self.body.apply_impulse_at_local_point(Vec2d(0, (((2-2*seg.alpha)-1)*30)/app.deltaTime)-currentVel*2, offset)
            draw.line(app.screen, "Yellow", app.convertCoordinates(origin), app.convertCoordinates((seg.point.x, seg.point.y)), 2)
            return True
        return False

    def render(self):
        super().render()
        app = self.app
        
        self.rect.center = app.convertCoordinates(self.body.position)
        self.image = pygame.transform.rotozoom(self.orig_image, math.degrees(self.body.angle), 1)
        
        self.rect = self.image.get_rect(center=self.rect.center)
        
        app.screen.blit(self.image, self.rect)