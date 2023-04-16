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
    maxAngularVelocity = math.pi*5

    stabilisationForce = 3500000
    stabilisationDampening = Vec2d(400, 2000)

    leftRayOffset = Vec2d(-35,0)
    rightRayOffset = Vec2d(35,0)
    
    rayDistance = 85

    rayAlpha = 1-50/rayDistance
    rayAlphaCrouch = 1-25/rayDistance

    jumpForce = 40000000
    crouchJumpMultiplier = 1.1

    jumpingCooldown = .1
    airControlCooldown = .02

    def __init__(self, app):
        super().__init__(app)
        
        # Physics
        self.body.position = app.screenSize.x/2, app.screenSize.y/2
        self.body.mass = 1
        self.body.moment = .1
        
        self.hoverboard = Poly.create_box(self.body, (100, 10))
        self.hoverboard.density = 0.6
        self.hoverboard.elasticity = 1
        self.hoverboard.friction = 1
        self.hoverboard.filter = pymunk.ShapeFilter(categories = PLAYER_CATEGORY)
        
        # Input
        self.jumpTick = self.jumpingCooldown
        self.jumpKey = False
        self.moveVector = Vector2(0,0)

        self.gliding = False

        self.crouch = False

        self.airControlTick = 0
        
        # Render
        self.image = pygame.Surface((100, 10), pygame.SRCALPHA)
        self.image.fill("Red")
        pygame.draw.rect(self.image, "black", Rect(0,0,5,10))
        self.rect = self.image.get_rect(center=app.convertCoordinates(self.body.position))
        self.orig_image = self.image
        
        app.space.add(self.body, self.hoverboard)
    
    def event(self, event):
        if DEBUG:
            self.debug_event(event)
        
        match event.type:
                case pygame.KEYDOWN:
                    match event.key:
                        case pygame.K_SPACE:
                            self.jump(True)
                        case pygame.K_q:
                            self.moveVector.x -= 1
                        case pygame.K_d:
                            self.moveVector.x += 1
                        case pygame.K_s:
                            self.crouch = True
                        case pygame.K_a:
                            self.gliding = True
                case pygame.KEYUP:
                    match event.key:
                        case pygame.K_SPACE:
                            self.jump(False)
                        case pygame.K_q:
                            self.moveVector.x += 1
                        case pygame.K_d:
                            self.moveVector.x -= 1
                        case pygame.K_s:
                            self.crouch = False
                        case pygame.K_a:
                            self.gliding = False

    def debug_event(self, event):
        match event.type:
                case pygame.KEYDOWN:
                    match event.key:
                        case pygame.K_r:
                            self.body.position = self.app.convertCoordinates(pygame.mouse.get_pos())
                            self.body.angle = 0
                        case pygame.K_t:
                            self.body.angular_velocity = 0
                            self.body.velocity = (0, 0)

    def jump(self, state):
        self.jumpKey = state
        if self.jumpTick > self.jumpingCooldown and state:
            self.jumpTick = 0

    def update(self):
        app = self.app

        distanceMultiplication = self.rayAlphaCrouch if self.crouch else self.rayAlpha
        jumpMultiplier = self.crouchJumpMultiplier if self.crouch else 1
        
        # leftDip = self.moveVector.x > 0

        # Left ray
        left = self.hoverRay(self.leftRayOffset, self.rayDistance)
        # Right ray
        right = self.hoverRay(self.rightRayOffset, self.rayDistance)
    
        floor = left or right
        if floor:
            self.airControlTick = 0
        else:
            self.airControlTick += app.deltaTime


        if self.jumpTick == 0 and floor:
            # self.body.apply_impulse_at_local_point((0,500000))
            if left:
                localNormal = self.body.world_to_local(self.body.position+left.normal)
                self.body.apply_force_at_local_point(localNormal*self.jumpForce*jumpMultiplier, (-35,0))
            if right:
                localNormal = self.body.world_to_local(self.body.position+right.normal)
                self.body.apply_force_at_local_point(localNormal*self.jumpForce*jumpMultiplier, (35,0))
        elif floor and self.jumpTick > self.jumpingCooldown: # Stick to floor
            if left:
                dip = 1 + (self.moveVector.x < 0) * .075

                origin = self.body.local_to_world(self.leftRayOffset)
                currentVel = self.body.world_to_local(origin+self.body.velocity_at_local_point(self.leftRayOffset))
                self.body.apply_force_at_local_point(Vec2d(0, (((2-2*left.alpha)-(2*dip*distanceMultiplication))*self.stabilisationForce))-Vec2d(currentVel.x*self.stabilisationDampening.x, currentVel.y*self.stabilisationDampening.y), self.leftRayOffset)
            if right:
                dip = 1 + (self.moveVector.x > 0) * .075

                origin = self.body.local_to_world(self.rightRayOffset)
                currentVel = self.body.world_to_local(origin+self.body.velocity_at_local_point(self.rightRayOffset))
                self.body.apply_force_at_local_point(Vec2d(0, (((2-2*right.alpha)-(2*dip*distanceMultiplication))*self.stabilisationForce))-Vec2d(currentVel.x*self.stabilisationDampening.x, currentVel.y*self.stabilisationDampening.y), self.rightRayOffset)
                
            self.body.apply_force_at_local_point((self.moveVector.x*1600000, 0))
        elif self.airControlTick > self.airControlCooldown:
            f = max if -self.moveVector.x > 0 else min
            if abs(f(self.body.angular_velocity, 0)) < self.maxAngularVelocity:
                self.body.angular_velocity += min(-self.moveVector.x*app.deltaTime*50, self.maxAngularVelocity-self.body.angular_velocity)

        self.jumpTick += app.deltaTime
        super().update()

    def hoverRay(self, offset, dist=100):
        app = self.app

        origin = self.body.local_to_world(offset)
        target = self.body.local_to_world(Vec2d(offset.x, -dist))

        seg = app.space.segment_query_first(origin, target, 2, self.mask)

        return seg

    def render(self):
        super().render()
        app = self.app
        
        self.rect.center = app.convertCoordinates(self.body.position)
        self.image = pygame.transform.rotozoom(self.orig_image, math.degrees(self.body.angle), 1)
        
        self.rect = self.image.get_rect(center=self.rect.center)
        
        app.screen.blit(self.image, self.rect)