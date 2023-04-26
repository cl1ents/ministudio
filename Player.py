from PhysicsObject import PhysicsObject
from Helpers import lerp, clamp, getPointAtAngle, addPoints
from easing_functions import CubicEaseInOut

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

def draw_line_round_corners(surf, c, p1, p2, w):
    pygame.draw.line(surf, c, p1, p2, w)
    if p1[0] > 0:
        pygame.draw.circle(surf, c, p1, w // 2)
    if p2[0] > 0:
        pygame.draw.circle(surf, c, p2, w // 2)

class Player(PhysicsObject):
    mask = pymunk.ShapeFilter(mask=pymunk.ShapeFilter.ALL_MASKS()^PLAYER_CATEGORY)
    maxAngularVelocity = math.pi*2.5

    stabilisationForce = 10000
    stabilisationDampening = Vec2d(1, 8)

    leftRayOffset = Vec2d(-35,0)
    rightRayOffset = Vec2d(35,0)
    
    rayDistance = 90

    rayAlpha = 1-50/rayDistance
    rayAlphaCrouch = 1-25/rayDistance

    moveForce = 4000

    jumpForce = 120000
    crouchJumpMultiplier = 1.1

    jumpingCooldown = .3
    airControlCooldown = .02

    dashCooldown = .5
    dashDuration = .2
    dashVelocity = 1200

    normalGravityLimit = 2000
    glidingGravityLimit = 200
    fastGravityLimit = 7000

    def __init__(self, app):
        super().__init__(app)
        
        # Physics
        self.body.position = 0, 1
        self.body.mass = 0
        
        self.hoverboard = Poly.create_box(self.body, (100, 10))
        self.hoverboard.density = 1
        self.hoverboard.elasticity = 0
        self.hoverboard.mass = .35
        self.hoverboard.friction = 1
        self.hoverboard.filter = pymunk.ShapeFilter(categories = PLAYER_CATEGORY)
        self.hoverboard.collision_type = COLLTYPE_PLAYER

        self.chara = pymunk.Segment(self.body, (0, 25), (0, 100), 20)
        self.chara.density = 1
        self.chara.mass = .65
        self.chara.filter = pymunk.ShapeFilter(categories = PLAYER_CATEGORY)
        self.chara.collision_type = COLLTYPE_PLAYER

        # Input
        self.jumpTick = self.jumpingCooldown
        self.jumpKey = False
        self.moveVector = Vector2(0,0)

        self.gliding = False
        self.gravityLimit = self.normalGravityLimit

        self.crouch = False

        self.stunTick = 0

        self.airControlTick = self.airControlCooldown

        self.dashTick = self.dashCooldown
        self.dashDirection = Vec2d(1,0)

        self.onGround = False
        
        # Render
        self.boundingBox = pygame.Surface((100, 10), pygame.SRCALPHA)
        self.boundingBox.fill("Red")
        pygame.draw.rect(self.boundingBox, "black", Rect(0,0,5,10))
        self.BBrect = self.boundingBox.get_rect(center=app.convertCoordinates(self.body.position))
        self.BBorig_image = self.boundingBox

        self.images = [
            pygame.image.load("res/img/idle.png").convert_alpha(), 
            pygame.image.load("res/img/crouch.png").convert_alpha(), 
            pygame.image.load("res/img/dash.png").convert_alpha(),
            pygame.image.load("res/img/jump.png").convert_alpha(), 
            pygame.image.load("res/img/fall.png").convert_alpha()
        ]

        self.imageIndex = 0
        self.image = self.images[self.imageIndex]
        self.rect = self.image.get_rect(center=app.convertCoordinates(self.body.local_to_world((0,150))))
        
        app.space.add(self.body, self.hoverboard, self.chara)

        self.debugLines = []
    
    def event(self, event):
        if DEBUG:
            self.debug_event(event)
        
        match event.type:
                case pygame.KEYDOWN:
                    match event.key:
                        case pygame.K_SPACE:
                            self.jump(True)
                        case pygame.K_z:
                            self.dash()
                        case pygame.K_q:
                            self.moveVector.x -= 1
                        case pygame.K_d:
                            self.moveVector.x += 1
                        case pygame.K_s:
                            self.setCrouch(True)
                        case pygame.K_a:
                            self.setGlide(True)
                case pygame.KEYUP:
                    match event.key:
                        case pygame.K_SPACE:
                            self.jump(False)
                        case pygame.K_q:
                            self.moveVector.x += 1
                        case pygame.K_d:
                            self.moveVector.x -= 1
                        case pygame.K_s:
                            self.setCrouch(False)
                        case pygame.K_a:
                            self.setGlide(False)

    def debug_event(self, event):
        match event.type:
                case pygame.KEYDOWN:
                    match event.key:
                        case pygame.K_r:
                            self.body.position = Vec2d(0, 1) #self.app.convertCoordinates(pygame.mouse.get_pos())
                            self.body.angle = 0
                        case pygame.K_t:
                            self.body.angular_velocity = 0
                            self.body.velocity = (0, 0)

    def jump(self, state):
        self.jumpKey = state
        if self.jumpTick > self.jumpingCooldown and state:
            self.jumpTick = 0
        
        if state and not self.onGround:
            self.gravityLimit = self.normalGravityLimit

    def dash(self):
        if self.dashTick > self.dashCooldown:
            self.dashTick = 0

    def stun(self, time):
        self.body.velocity = 0, self.body.velocity.y
        self.stunTick = -time

    def setCrouch(self, state):
        self.crouch = state
        if state and not self.onGround:
            self.gravityLimit = self.fastGravityLimit
            self.body.velocity = (self.body.velocity.x, math.min(self.body.velocity.y, -750))
    
    def setGlide(self, state):
        self.gliding = state
        if state and not self.onGround:
            self.gravityLimit = self.glidingGravityLimit

    def update(self):
        app = self.app
        moveVector = self.moveVector

        onGround = True

        if self.stunTick < 0:
            self.jumpTick = self.jumpingCooldown+1
            self.dashTick = self.dashCooldown+1
            moveVector = Vector2(0,0)

        self.stunTick += app.deltaTime

        distanceMultiplication = (self.rayAlphaCrouch if self.crouch else self.rayAlpha) + math.sin(app.time*3)*.075
        jumpMultiplier = self.crouchJumpMultiplier if self.crouch else 1
        
        # leftDip = self.moveVector.x > 0
        self.debugLines = []
        # Left ray
        left = self.hoverRay(self.leftRayOffset, self.rayDistance)
        # Right ray
        right = self.hoverRay(self.rightRayOffset, self.rayDistance)
        # Center ray
        center = self.hoverRay(Vec2d(0,0), self.rayDistance*2)
    
        if DEBUG:
            if left:
                self.debugLines.append([self.body.local_to_world(self.leftRayOffset), left.point])
            if right:
                self.debugLines.append([self.body.local_to_world(self.rightRayOffset), right.point])
            if center:
                self.debugLines.append([self.body.local_to_world((0,0)), center.point])

        floor = left or right
        if floor:
            self.airControlTick = 0
        else:
            self.airControlTick += app.deltaTime

        if self.dashTick == 0:
            self.dashDirection = (app.convertCoordinatesFromScreen(pygame.mouse.get_pos())-self.body.position).normalized()
            self.body.velocity *= .6
            self.body.velocity += self.dashDirection*self.dashVelocity
        
        
        self.debugLines.append([self.body.position, self.body.position+self.dashDirection*100])

        if self.jumpTick == 0 and floor:
            onGround = False
            if left:
                localNormal = self.body.world_to_local(self.body.position+left.normal)
                self.body.apply_force_at_local_point(localNormal*self.jumpForce*jumpMultiplier*.5, (-35,0))
            if right:
                localNormal = self.body.world_to_local(self.body.position+right.normal)
                self.body.apply_force_at_local_point(localNormal*self.jumpForce*jumpMultiplier*.5, (35,0))
        elif floor and self.jumpTick > self.jumpingCooldown: # Stick to floor
            if left:
                dip = 1 + (moveVector.x < 0) * .05

                origin = self.body.local_to_world(self.leftRayOffset)
                currentVel = self.body.world_to_local(origin+self.body.velocity_at_local_point(self.leftRayOffset))
                
                localNormal = self.body.world_to_local(self.body.position+left.normal)
                # localNormal = Vec2d(0,1)
                
                toApply = localNormal*(((2-2*left.alpha)-(2*dip*distanceMultiplication))*self.stabilisationForce)-Vec2d(currentVel.x*self.stabilisationDampening.x, currentVel.y*self.stabilisationDampening.y)
                self.body.apply_force_at_local_point(toApply*.4, self.leftRayOffset)
                self.body.apply_force_at_local_point(toApply*.6, (self.leftRayOffset.x, self.body.center_of_gravity.y))
            if right:
                dip = 1 + (moveVector.x > 0) * .05

                origin = self.body.local_to_world(self.rightRayOffset)
                currentVel = self.body.world_to_local(origin+self.body.velocity_at_local_point(self.rightRayOffset))
                
                localNormal = self.body.world_to_local(self.body.position+right.normal)
                # localNormal = Vec2d(0,1)
                
                toApply = localNormal*(((2-2*right.alpha)-(2*dip*distanceMultiplication))*self.stabilisationForce)-Vec2d(currentVel.x*self.stabilisationDampening.x, currentVel.y*self.stabilisationDampening.y)
                self.body.apply_force_at_local_point(toApply*.4, self.rightRayOffset)
                self.body.apply_force_at_local_point(toApply*.6, (self.rightRayOffset.x, self.body.center_of_gravity.y))
            
            toApply = Vec2d(moveVector.x*self.moveForce, 0)
            self.body.apply_force_at_local_point(toApply*.3, (0, self.body.center_of_gravity.y*1.4))
            self.body.apply_force_at_local_point(toApply*.7)
        elif self.airControlTick > self.airControlCooldown:
            onGround = False
            f = max if -moveVector.x > 0 else min
            if abs(f(self.body.angular_velocity, 0)) < self.maxAngularVelocity:
                self.body.angular_velocity += min(-moveVector.x*app.deltaTime*50, self.maxAngularVelocity-self.body.angular_velocity)
        else:
            onGround = False
        
        if right or left:
            count = (1 if right else 0) + (1 if left else 0)
            rightAngle = Vec2d(0,1).rotated(self.body.angle).get_angle_between(right.normal) if right else 0
            leftAngle = Vec2d(0,1).rotated(self.body.angle).get_angle_between(left.normal) if left else 0
            angle = (rightAngle+leftAngle)/count

            fullAngle = angle # Vec2d(0,1).rotated(self.body.angle).get_angle_between(Vec2d(0,1).rotated(angle))
            self.body.angular_velocity += ((fullAngle)/app.deltaTime)*.004*(count/2)
        elif center and not self.gliding:
            fullAngle = Vec2d(0,1).rotated(self.body.angle).get_angle_between(center.normal)
            self.body.angular_velocity += ((fullAngle)/app.deltaTime)*.002
            self.body.angular_velocity *= .95
        elif self.gliding:
            fullAngle = Vec2d(0,1).rotated(self.body.angle).get_angle_between(Vec2d(0,1))
            self.body.angular_velocity += ((fullAngle)/app.deltaTime)*.02
            self.body.angular_velocity *= .95

        self.body.velocity = self.body.velocity.x, max(self.body.velocity.y, -self.gravityLimit)

        if onGround:
            self.imageIndex = 1 if self.crouch else 0
            self.gravityLimit = self.normalGravityLimit
        else:
            self.imageIndex = 3 if self.body.velocity.y > 50 else 4
        
        self.imageIndex = 2 if self.dashTick < self.dashDuration else self.imageIndex

        if self.crouch and self.chara.b == (0, 100):
            self.chara.unsafe_set_endpoints(self.chara.a, (0, 65))
        elif not self.crouch and self.chara.b == (0, 65):
            self.chara.unsafe_set_endpoints(self.chara.a, (0, 100))

        self.jumpTick += app.deltaTime
        self.dashTick += app.deltaTime

        self.onGround = onGround

        super().update()

    def hoverRay(self, offset, dist=100):
        app = self.app

        origin = self.body.local_to_world(offset)
        localvel = self.body.world_to_local(self.body.position+self.body.velocity)
        target = self.body.local_to_world(Vec2d(offset.x+localvel.x*app.deltaTime*10, -dist))

        seg = app.space.segment_query_first(origin, target, 2, self.mask)

        return seg

    def render(self):
        super().render()
        app = self.app
        
        if DEBUG:
            self.BBrect.center = app.convertCoordinates(self.body.position)
            self.boundingBox = pygame.transform.rotozoom(self.BBorig_image, math.degrees(self.body.angle), 1)
            
            self.BBrect = self.boundingBox.get_rect(center=self.BBrect.center)
            
            app.screen.blit(self.boundingBox, self.BBrect)

            draw_line_round_corners(app.screen, (255, 0, 0), app.convertCoordinates(self.body.local_to_world(self.chara.a)), app.convertCoordinates(self.body.local_to_world(self.chara.b)), int(self.chara.radius*2))

            for line in self.debugLines:
                pygame.draw.line(app.screen, "Red", *[app.convertCoordinates(e) for e in line], 1)

            speed = app.comicsans.render(f"SPEED: {int(self.body.velocity.get_distance((0,0)) or 0)}", False, (0,0,0))
            # speed = pygame.transform.rotate(speed, math.degrees(self.body.angle))
            rect = speed.get_rect(center=app.convertCoordinates(self.body.local_to_world((0,-25))))
            app.screen.blit(speed, rect)

        self.rect.center = app.convertCoordinates(self.body.local_to_world((0,75)))
        self.image = pygame.transform.smoothscale(self.images[self.imageIndex], (175,175))
        self.image = pygame.transform.rotate(self.image, math.degrees(self.body.angle))
        
        self.rect = self.image.get_rect(center=self.rect.center)
        app.screen.blit(self.image, self.rect)

